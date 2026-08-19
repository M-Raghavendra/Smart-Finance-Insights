/* =========================================================
   Analytics Dashboard — Chart.js Visualizations (Multi-Tab & Goal-Expense)
========================================================= */

document.addEventListener("DOMContentLoaded", function () {
    if (!window.analyticsData) return;

    const data = window.analyticsData;

    const palette = [
        "#2563EB", "#16A34A", "#D97706", "#9333EA", "#06B6D4",
        "#EC4899", "#8B5CF6", "#F59E0B", "#10B981", "#6366F1"
    ];

    // Helper function for line chart config
    function getLineChartConfig(labels, income, expenses, savings) {
        return {
            type: "line",
            data: {
                labels: labels,
                datasets: [
                    {
                        label: "Income (₹)",
                        data: income,
                        borderColor: "#16A34A",
                        backgroundColor: "rgba(22, 163, 74, 0.08)",
                        borderWidth: 2.5,
                        tension: 0.3,
                        fill: true
                    },
                    {
                        label: "Expenses (₹)",
                        data: expenses,
                        borderColor: "#DC2626",
                        backgroundColor: "rgba(220, 38, 38, 0.08)",
                        borderWidth: 2.5,
                        tension: 0.3,
                        fill: true
                    },
                    {
                        label: "Savings (₹)",
                        data: savings,
                        borderColor: "#2563EB",
                        backgroundColor: "rgba(37, 99, 235, 0.08)",
                        borderWidth: 2.5,
                        tension: 0.3,
                        fill: true
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: "top", labels: { font: { size: 12 } } },
                    tooltip: {
                        callbacks: {
                            label: function (ctx) {
                                return ` ${ctx.dataset.label}: ₹${ctx.raw.toLocaleString()}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { callback: function (val) { return "₹" + val.toLocaleString(); } }
                    }
                }
            }
        };
    }

    // 1. Overview Tab Cash Flow Line Chart
    const overviewCashCtx = document.getElementById("overviewCashFlowChart");
    if (overviewCashCtx && data.trendLabels) {
        new Chart(overviewCashCtx, getLineChartConfig(data.trendLabels, data.trendIncome, data.trendExpenses, data.trendSavings));
    }

    // 2. Spending Analysis Tab Doughnut Chart
    const doughnutCtx = document.getElementById("categoryDoughnutChart");
    if (doughnutCtx && data.categories && data.categories.length > 0) {
        new Chart(doughnutCtx, {
            type: "doughnut",
            data: {
                labels: data.categories,
                datasets: [{
                    data: data.categoryAmounts,
                    backgroundColor: palette.slice(0, data.categories.length),
                    borderWidth: 2,
                    borderColor: "#ffffff"
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: "bottom", labels: { font: { size: 12 } } },
                    tooltip: {
                        callbacks: {
                            label: function (ctx) {
                                return ` ${ctx.label}: ₹${ctx.raw.toLocaleString()}`;
                            }
                        }
                    }
                }
            }
        });
    }

    // 3. Monthly Spending Trend (Last 6 Months) Bar Chart
    const monthlyTrendCtx = document.getElementById("monthlyTrendChart");
    if (monthlyTrendCtx && data.monthlyTrend6mLabels) {
        new Chart(monthlyTrendCtx, {
            type: "bar",
            data: {
                labels: data.monthlyTrend6mLabels,
                datasets: [{
                    label: "Monthly Expenses (₹)",
                    data: data.monthlyTrend6mAmounts,
                    backgroundColor: "#2563EB",
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: function (ctx) {
                                return ` Expenses: ₹${ctx.raw.toLocaleString()}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { callback: function (val) { return "₹" + val.toLocaleString(); } }
                    }
                }
            }
        });
    }

    // 4. Weekly Spending Pattern (Current Month) Bar Chart
    const weeklyPatternCtx = document.getElementById("weeklyPatternChart");
    if (weeklyPatternCtx && data.weeklyLabels) {
        new Chart(weeklyPatternCtx, {
            type: "bar",
            data: {
                labels: data.weeklyLabels,
                datasets: [{
                    label: "Weekly Expenses (₹)",
                    data: data.weeklyAmounts,
                    backgroundColor: "#8B5CF6",
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: function (ctx) {
                                return ` Expenses: ₹${ctx.raw.toLocaleString()}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { callback: function (val) { return "₹" + val.toLocaleString(); } }
                    }
                }
            }
        });
    }

    // 5. Goal-Related Expenses by Goal (Bar Chart)
    const goalExpCtx = document.getElementById("goalExpensesChart");
    if (goalExpCtx && data.goalNames && data.goalNames.length > 0) {
        new Chart(goalExpCtx, {
            type: "bar",
            data: {
                labels: data.goalNames,
                datasets: [{
                    label: "Total Goal Expenses (₹)",
                    data: data.goalLinkedTotals,
                    backgroundColor: palette.slice(0, data.goalNames.length),
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: function (ctx) {
                                return ` Linked Expenses: ₹${ctx.raw.toLocaleString()}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { callback: function (val) { return "₹" + val.toLocaleString(); } }
                    }
                }
            }
        });
    }

    // 6. Expense Distribution (Goal-Linked vs Regular Non-Goal Expenses Doughnut Chart)
    const goalVsRegCtx = document.getElementById("goalVsRegularChart");
    if (goalVsRegCtx) {
        new Chart(goalVsRegCtx, {
            type: "doughnut",
            data: {
                labels: ["Goal-Linked Expenses", "Regular Expenses"],
                datasets: [{
                    data: [data.totalGoalLinked || 0, data.totalRegularExpenses || 0],
                    backgroundColor: ["#2563EB", "#94A3B8"],
                    borderWidth: 2,
                    borderColor: "#ffffff"
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: "bottom", labels: { font: { size: 12 } } },
                    tooltip: {
                        callbacks: {
                            label: function (ctx) {
                                return ` ${ctx.label}: ₹${ctx.raw.toLocaleString()}`;
                            }
                        }
                    }
                }
            }
        });
    }

    // 7. Monthly Goal-Linked Expense Trend (Line/Bar Chart)
    const monthlyGoalTrendCtx = document.getElementById("monthlyGoalExpenseTrendChart");
    if (monthlyGoalTrendCtx && data.monthlyGoalTrendLabels) {
        new Chart(monthlyGoalTrendCtx, {
            type: "line",
            data: {
                labels: data.monthlyGoalTrendLabels,
                datasets: [{
                    label: "Monthly Goal-Linked Expenses (₹)",
                    data: data.monthlyGoalTrendAmounts,
                    borderColor: "#2563EB",
                    backgroundColor: "rgba(37, 99, 235, 0.1)",
                    borderWidth: 2.5,
                    tension: 0.3,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: "top", labels: { font: { size: 12 } } },
                    tooltip: {
                        callbacks: {
                            label: function (ctx) {
                                return ` Goal Expenses: ₹${ctx.raw.toLocaleString()}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { callback: function (val) { return "₹" + val.toLocaleString(); } }
                    }
                }
            }
        });
    }

    // 8. Trends & Predictions Tab Line Chart
    const trendsCashCtx = document.getElementById("trendsCashFlowChart");
    if (trendsCashCtx && data.trendLabels) {
        new Chart(trendsCashCtx, getLineChartConfig(data.trendLabels, data.trendIncome, data.trendExpenses, data.trendSavings));
    }
});
