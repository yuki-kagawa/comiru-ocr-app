const colors = [
  'rgba(100, 149, 237, 0.8)', // Cornflower Blue
  'rgba(144, 238, 144, 0.8)', // Light Green
  'rgba(255, 182, 193, 0.8)', // Light Pink
  'rgba(255, 160, 122, 0.8)', // Light Salmon
  'rgba(221, 160, 221, 0.8)', // Plum
  'rgba(175, 238, 238, 0.8)'  // Pale Turquoise
];

const labels = JSON.parse(document.getElementById('chart-labels').textContent);
const rawData = JSON.parse(document.getElementById('chart-data').textContent);

const datasets = rawData.map((item, index) => ({
  label: item.label,  // 教科名
  data: item.data,    // 日別スコア
  borderColor: colors[index % colors.length],
  backgroundColor: colors[index % colors.length],
  tension: 0.3,
  spanGaps: true  // ← データがない日も線をつなげる
}));

const ctx = document.getElementById('lineChart').getContext('2d');

new Chart(ctx, {
    type: 'line',
    data: {
        labels: labels,
        datasets: datasets
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: true },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        const label = context.dataset.label || '';
                        const value = context.raw != null ? context.raw.toFixed(2) : 'N/A';
                        return `${label}: ${value}`;
                    }
                }
            }
        },
        scales: {
            x: {
                type: 'category',
                grid: {
                    display: false
                },
                ticks: {
                  maxRotation: 0,
                  callback: function(value, index) {
                    return labels[index];  // ← ここで "1日" などを明示的に返す
                  }
                }
            },
            y: {
                beginAtZero: true,
                suggestedMax: 5,
                ticks: {
                    stepSize: 1,  // ← ラベルを1単位で表示
                    callback: function(value) {
                        return value.toFixed(0); // 小数点なしで表示（整数のみ）
                    }
                },
                grid: {
                    drawTicks: true,
                    drawBorder: true,
                    color: '#ddd'  // 罫線の色を薄く
                }
            }
        }
    }
});
