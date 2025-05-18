// Sample Data for the chart and progress bar
const riceAvailabilityData = {
    available: 70,
    unavailable: 30
};

// Display the rice availability chart
const ctx = document.getElementById('riceAvailabilityChart').getContext('2d');
const riceAvailabilityChart = new Chart(ctx, {
    type: 'pie',
    data: {
        labels: ['Available Rice', 'Unavailable Rice'],
        datasets: [{
            label: 'Rice Availability',
            data: [riceAvailabilityData.available, riceAvailabilityData.unavailable],
            backgroundColor: ['#4CAF50', '#FFC107'],
        }]
    }
});

// Progress Bar (can be dynamic)
function updateProgressBar(percentage) {
    const progressBar = document.querySelector('.progress-bar');
    progressBar.style.width = percentage + '%';
    progressBar.textContent = percentage + '% Completed';
}

// Update progress bar for Zero Hunger
updateProgressBar(75);  // Example: Set progress to 75%

