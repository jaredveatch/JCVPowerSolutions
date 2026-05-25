document.addEventListener('DOMContentLoaded', function() {
    // Fetch and display data for the dashboard
    fetch('/api/dashboard-data/')
        .then(response => response.json())
        .then(data => {
            document.getElementById('total-customers').innerText = data.total_customers;
            document.getElementById('total-jobs').innerText = data.total_jobs;
            document.getElementById('total-estimates').innerText = data.total_estimates;
            document.getElementById('total-invoices').innerText = data.total_invoices;
            // Populate recent activity
            const activityList = document.getElementById('activity-list');
            data.recent_activity.forEach(activity => {
                const li = document.createElement('li');
                li.innerText = activity;
                activityList.appendChild(li);
            });
        });
});