document.addEventListener('DOMContentLoaded', function () {
    // vsinData should be already parsed from the vsinDataStr in your main script tag
    if (typeof vsinData === 'undefined') {
        console.error('vsinData is not defined');
        return;
    }

    if (vsinData && vsinData['VSIN Team 1'] && vsinData['VSIN Team 2']) {
        const team1 = vsinData['VSIN Team 1'];
        const team2 = vsinData['VSIN Team 2'];

        const handleData = [parseFloat(vsinData['Handle Team 1']), parseFloat(vsinData['Handle Team 2'])];
        const betsData = [parseFloat(vsinData['Bets Team 1']), parseFloat(vsinData['Bets Team 2'])];

        const config = (data, title) => ({
            type: 'pie',
            data: {
                labels: [team1, team2],
                datasets: [{
                    label: title,
                    data: data,
                    backgroundColor: ['rgba(255, 99, 132, 0.2)', 'rgba(54, 162, 235, 0.2)'],
                    borderColor: ['rgba(255, 99, 132, 1)', 'rgba(54, 162, 235, 1)'],
                    borderWidth: 1,
                }],
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: true,
                        text: title,
                    },
                    datalabels: {
                        color: '#000000', // Label color
                        font: {
                            weight: 'bold'
                        },
                        formatter: (value, context) => {
                            let sum = 0;
                            let dataArr = context.chart.data.datasets[0].data;
                            dataArr.map(data => {
                                sum += data;
                            });
                            let percentage = (value * 100 / sum).toFixed(0) + "%";
                            return percentage;
                        }
                    }
                },
            },
            plugins: [ChartDataLabels]
        });

        // Ensure chart elements exist and have valid IDs before creating the charts
        const handleChartElement = document.getElementById('vsinHandleChart');
        const betsChartElement = document.getElementById('vsinBetsChart');

        if (handleChartElement && handleChartElement.id !== '0') {
            const handleCtx = handleChartElement.getContext('2d');
            new Chart(handleCtx, config(handleData, 'Money Wagered'));
        } else {
            console.error('Handle chart element is missing or has invalid ID.');
        }

        if (betsChartElement && betsChartElement.id !== '0') {
            const betsCtx = betsChartElement.getContext('2d');
            new Chart(betsCtx, config(betsData, '# of Bets'));
        } else {
            console.error('Bets chart element is missing or has invalid ID.');
        }
    } else {
        console.error('VSIN data is missing or incomplete.');
        console.log('VSIN data provided:', vsinData);
    }
});
