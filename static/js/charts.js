// Скрипты для графиков успеваемости

// Инициализация графика успеваемости группы
function initGradeChart(chartId, apiUrl, groupSelectId) {
    const ctx = document.getElementById(chartId).getContext('2d');
    let chart = null;
    
    function loadChartData() {
        const groupId = document.getElementById(groupSelectId).value;
        
        if (!groupId) {
            return;
        }
        
        // Показываем индикатор загрузки
        showLoading();
        
        fetch(`${apiUrl}?group_id=${groupId}`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    showError(data.error);
                    return;
                }
                
                // Если график уже существует, уничтожаем его
                if (chart) {
                    chart.destroy();
                }
                
                // Создаём новый график
                chart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: data.labels,
                        datasets: data.datasets.map(ds => ({
                            ...ds,
                            borderWidth: 2,
                            borderRadius: 5,
                            barPercentage: 0.8,
                            categoryPercentage: 0.7
                        }))
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                position: 'top',
                                labels: {
                                    font: {
                                        size: 12
                                    }
                                }
                            },
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
                                        let label = context.dataset.label || '';
                                        let value = context.parsed.y;
                                        if (value > 0) {
                                            return `${label}: ${value}`;
                                        } else {
                                            return `${label}: оценок нет`;
                                        }
                                    }
                                }
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                max: 5,
                                title: {
                                    display: true,
                                    text: 'Оценка',
                                    font: {
                                        size: 14,
                                        weight: 'bold'
                                    }
                                },
                                ticks: {
                                    stepSize: 1,
                                    callback: function(value) {
                                        return value + ' балл(ов)';
                                    }
                                }
                            },
                            x: {
                                title: {
                                    display: true,
                                    text: 'Студенты',
                                    font: {
                                        size: 14,
                                        weight: 'bold'
                                    }
                                },
                                ticks: {
                                    rotation: 45,
                                    autoSkip: true,
                                    maxRotation: 45,
                                    minRotation: 45
                                }
                            }
                        },
                        title: {
                            display: true,
                            text: `Успеваемость группы ${data.group_name || ''}`,
                            font: {
                                size: 16,
                                weight: 'bold'
                            }
                        }
                    }
                });
                
                hideLoading();
                
                // Обновляем информацию о группе
                updateGroupInfo(data);
            })
            .catch(error => {
                console.error('Ошибка загрузки данных:', error);
                showError('Ошибка загрузки данных графика');
                hideLoading();
            });
    }
    
    // Загружаем данные при изменении группы
    document.getElementById(groupSelectId).addEventListener('change', loadChartData);
    
    // Загружаем начальные данные
    if (document.getElementById(groupSelectId).value) {
        loadChartData();
    }
    
    // Функция обновления информации о группе
    function updateGroupInfo(data) {
        const infoDiv = document.getElementById('group-info');
        if (infoDiv && data.group_name) {
            infoDiv.innerHTML = `
                <div class="alert alert-info">
                    <strong>Группа:</strong> ${data.group_name}<br>
                    <strong>Всего студентов:</strong> ${data.labels.length}
                </div>
            `;
        }
    }
}

// Функция для создания графика успеваемости по предметам (пирог/круговая)
function initSubjectPieChart(chartId, data) {
    const ctx = document.getElementById(chartId).getContext('2d');
    
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: data.labels,
            datasets: [{
                data: data.values,
                backgroundColor: [
                    '#28a745',  // 5 - зелёный
                    '#17a2b8',  // 4 - голубой
                    '#ffc107',  // 3 - жёлтый
                    '#dc3545'   // 2 - красный
                ],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.label || '';
                            let value = context.parsed;
                            let total = context.dataset.data.reduce((a, b) => a + b, 0);
                            let percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

// Функция для создания линейного графика (динамика успеваемости)
function initLineChart(chartId, data) {
    const ctx = document.getElementById(chartId).getContext('2d');
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: data.datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top'
                },
                title: {
                    display: true,
                    text: 'Динамика успеваемости по месяцам'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 5,
                    title: {
                        display: true,
                        text: 'Средний балл'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Месяцы'
                    }
                }
            }
        }
    });
}

// Вспомогательные функции
function showLoading() {
    let spinner = document.querySelector('.spinner-overlay');
    if (!spinner) {
        spinner = document.createElement('div');
        spinner.className = 'spinner-overlay';
        spinner.innerHTML = '<div class="spinner-border text-light" role="status"><span class="visually-hidden">Загрузка...</span></div>';
        document.body.appendChild(spinner);
    }
    spinner.style.display = 'flex';
}

function hideLoading() {
    const spinner = document.querySelector('.spinner-overlay');
    if (spinner) {
        spinner.style.display = 'none';
    }
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'alert alert-danger alert-dismissible fade show';
    errorDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.querySelector('.container').insertAdjacentElement('afterbegin', errorDiv);
    
    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}

// Экспорт графика в изображение
function exportChartAsImage(chartId, filename = 'chart.png') {
    const canvas = document.getElementById(chartId);
    if (!canvas) return;
    
    const link = document.createElement('a');
    link.download = filename;
    link.href = canvas.toDataURL();
    link.click();
}

// Обновление графика при изменении данных
function refreshChart(chart, newData) {
    if (chart) {
        chart.data = newData;
        chart.update();
    }
}
