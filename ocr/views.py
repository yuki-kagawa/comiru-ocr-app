from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from PIL import Image
import pytesseract
import re
from .models import LessonEvaluation
from difflib import get_close_matches
from collections import defaultdict
from django.db.models import Avg
from datetime import datetime, date
import calendar
from dateutil.relativedelta import relativedelta

@login_required
def dashboard(request):
    # セッションから選択中の子供IDを取得
    child_id = request.session.get('selected_child_id')
    if not child_id:
        return redirect('accounts:mypage')

    # 1. 対象月を取得（クエリパラメータ or 今月）
    month_str = request.GET.get('month')
    if month_str:
        try:
            target_month = datetime.strptime(month_str, "%Y-%m")
        except ValueError:
            target_month = datetime.now()
    else:
        target_month = datetime.now()

    year = target_month.year
    month = target_month.month

    # 2. 月の日付リスト作成
    last_day = calendar.monthrange(year, month)[1]
    date_list = [date(year, month, day) for day in range(1, last_day + 1)]
    chart_labels = [f"{d.day}日" for d in date_list]

    # 3. 子供ID付きで対象月のデータ取得（教科ごと）
    records = (
        LessonEvaluation.objects
        .filter(date__year=year, date__month=month, child_id=child_id)
        .values('subject', 'date')
        .annotate(avg_rating=Avg('rating'))
    )

    # 4. 教科ごとの日付→スコア辞書を作成
    subject_data = defaultdict(dict)
    for r in records:
        subject = r['subject']
        record_date = r['date']
        avg = r['avg_rating']
        subject_data[subject][record_date] = avg

    # 5. 教科ごとの line_chart_data 構造を作成（None補完）
    line_chart_data = []
    for subject, data_by_date in subject_data.items():
        data_list = [data_by_date.get(d, None) for d in date_list]
        line_chart_data.append({
            'label': subject,
            'data': data_list
        })

    # 前月・次月の文字列を計算
    prev_month = (target_month - relativedelta(months=1)).strftime("%Y-%m")
    next_month = (target_month + relativedelta(months=1)).strftime("%Y-%m")

    return render(request, 'ocr/dashboard.html', {
        'labels': chart_labels,
        'line_chart_data': line_chart_data,
        'selected_month': target_month.strftime("%Y-%m"),
        'prev_month': prev_month,  # 追加
        'next_month': next_month,  # 追加
    })

# 登録済の講師名一覧（DBや定数に保存）
known_teachers = ['笠井伸春', '佐藤健太', '田中花子', '鈴木一郎']

def correct_teacher_name(name_candidate):
    # 類似度の高い名前を探す
    matches = get_close_matches(name_candidate, known_teachers, n=1, cutoff=0.5)
    return matches[0] if matches else name_candidate

def normalize_text(text):
    replacements = {
        '①': '1', '②': '2', '③': '3', '④': '4', '⑤': '5', '⑥': '6', '⑦': '7', '⑧': '8', '⑨': '9', '⑩': '10',
        '０': '0', '１': '1', '２': '2', '３': '3', '４': '4', '５': '5', '６': '6', '７': '7', '８': '8', '９': '9',
        '〜': '-', 'ー': '-', '—': '-', '−': '-', '―': '-', '～': '-',
        '貫': '★', '責': '★', '費': '★', '貴': '★', 'ま': 'ま',
        ' ': '',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

def extract_teacher_name(raw_text):
    for line in raw_text.splitlines():
        if "書いた講師" in line:
            match = re.search(r"書いた講師.{1}(.+)", line)
            if match:
                name = match.group(1).replace(" ", "").strip()
                return correct_teacher_name(name)
    return None

def parse_rating(stars):
    star_count = 0.0
    for ch in stars:
        if ch == '★':
            star_count += 1
        elif ch == 'ま':
            star_count += 0.5
        elif ch in ['貫', '責', '費']:  # 0.5の候補とする
            star_count += 0.5
    return star_count if star_count > 0 else None

def extract_date(text):
    match = re.search(r'授業日(\d{1,2})/(\d{1,2})[-~〜]', text)
    if match:
        now = datetime.now()
        year = now.year
        month = int(match.group(1))
        day = int(match.group(2))
        try:
            date_obj = datetime(year, month, day)
            return date_obj.strftime('%Y-%m-%d')
        except ValueError:
            return ''  # 日付が不正な場合は空文字返す
    return ''



def extract_table_data(text):
    lines = text.splitlines()
    data = []

    current_subject = ''

    for line in lines:
        # 教科の特定
        if '英語' in line:
            current_subject = '英語'
        elif '数学' in line:
            current_subject = '数学'
        elif '理科' in line:
            current_subject = '理科'
        elif '社会' in line:
            current_subject = '社会'

        # 内容とページ
        m = re.search(r'(.*?)p(\d{2,3}(?:[-~〜]?\d{2,3})?)', line)
        if not m:
            continue

        content = m.group(1).strip()
        page = 'p' + m.group(2)

        # ★評価の抽出
        symbols = re.findall(r'[★ま]', line)
        if not symbols:
            continue

        rating = 0
        for s in symbols:
            if s == '★':
                rating += 1.0
            elif s == 'ま':
                rating += 0.5

        data.append([current_subject, content, page, rating])

    return data


def img_upload(request):
    if request.method == 'POST' and request.FILES.get('document'):
        document = request.FILES['document']

        try:
            # メモリ上で画像オープン＆リサイズ・変換
            img = Image.open(document)
            img = img.convert('RGB')  # 形式統一

            # OCR
            raw_text = pytesseract.image_to_string(img, lang='jpn')
            raw_text = normalize_text(raw_text)

            # データ抽出
            teacher_name = extract_teacher_name(raw_text)
            lesson_date = extract_date(raw_text)
            data = extract_table_data(raw_text)

            # 子供チェック
            child_id = request.session.get('selected_child_id')
            if not child_id:
                messages.error(request, "お子様が選択されていません。")
                return redirect('accounts:mypage')

            # DB保存
            for row in data:
                try:
                    LessonEvaluation.objects.create(
                        date=lesson_date,
                        subject=row[0],
                        content=row[1],
                        page=row[2],
                        rating=row[3],
                        teacher=teacher_name,
                        child_id=child_id
                    )
                except Exception as e:
                    print("保存エラー:", e)

            return render(request, 'ocr/img_upload_result.html', {
                'text': raw_text,
                'table_data': data,
                'teacher_name': teacher_name,
                'date': lesson_date,
            })

        except Exception as e:
            messages.error(request, f"OCR処理中にエラーが発生しました: {str(e)}")
            return redirect('ocr:img_upload')

    return render(request, 'ocr/img_upload.html')
