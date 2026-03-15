// Initialize selected instances
let selectedInstances = {
    'aws-ec2': null,
    'aws-rds': null,
    'gcp-instances': null
};

// Load data and initialize charts
$(document).ready(function() {
    loadData();

    // Set up refresh button
    $('#refresh-data').click(function() {
        $.get('/refresh', function(response) {
            if (response.status === 'success') {
                loadData();
            }
        });
    });
});

function loadData() {
    $.get('/api/metrics', function(data) {
        updateLastUpdated(data.timestamp);
        loadAWS_EC2Instances();
        loadAWS_RDSInstances();
        loadGCPInstances();
    });
}

function updateLastUpdated(timestamp) {
    const date = new Date(timestamp);
    $('#last-updated').text('Last updated: ' + date.toLocaleString());
}

function loadAWS_EC2Instances() {
    $.get('/api/aws/ec2', function(instances) {
        const container = $('#aws-ec2-instances');
        container.empty();

        Object.keys(instances).forEach(function(instanceId) {
            const instance = instances[instanceId];
            const instanceElem = $('<div class="instance-item"></div>')
                .data('id', instanceId)
                .append(`<span class="instance-id">${instanceId}</span>`)
                .append(`<span class="instance-type">Type: ${instance.type}</span>`)
                .append(`<span class="instance-status">Status: ${instance.state}</span>`);

            instanceElem.click(function() {
                $('.instance-item', container).removeClass('selected');
                $(this).addClass('selected');
                selectedInstances['aws-ec2'] = instanceId;
                loadAWS_EC2Metrics(instanceId);
            });

            container.append(instanceElem);
        });

        if (Object.keys(instances).length > 0) {
            const firstInstanceId = Object.keys(instances)[0];
            $(`#aws-ec2-instances .instance-item`).first().addClass('selected');
            selectedInstances['aws-ec2'] = firstInstanceId;
            loadAWS_EC2Metrics(firstInstanceId);
        }
    });
}

function loadAWS_RDSInstances() {
    $.get('/api/aws/rds', function(instances) {
        const container = $('#aws-rds-instances');
        container.empty();

        Object.keys(instances).forEach(function(instanceId) {
            const instance = instances[instanceId];
            const instanceElem = $('<div class="instance-item"></div>')
                .data('id', instanceId)
                .append(`<span class="instance-id">${instanceId}</span>`)
                .append(`<span class="instance-type">Engine: ${instance.engine}</span>`)
                .append(`<span class="instance-status">Status: ${instance.status}</span>`);

            instanceElem.click(function() {
                $('.instance-item', container).removeClass('selected');
                $(this).addClass('selected');
                selectedInstances['aws-rds'] = instanceId;
                loadAWS_RDSMetrics(instanceId);
            });

            container.append(instanceElem);
        });

        if (Object.keys(instances).length > 0) {
            const firstInstanceId = Object.keys(instances)[0];
            $(`#aws-rds-instances .instance-item`).first().addClass('selected');
            selectedInstances['aws-rds'] = firstInstanceId;
            loadAWS_RDSMetrics(firstInstanceId);
        }
    });
}

function loadGCPInstances() {
    $.get('/api/gcp/instances', function(instances) {
        const container = $('#gcp-instances');
        container.empty();

        Object.keys(instances).forEach(function(instanceId) {
            const instance = instances[instanceId];
            const instanceElem = $('<div class="instance-item"></div>')
                .data('id', instanceId)
                .append(`<span class="instance-id">${instanceId}</span>`)
                .append(`<span class="instance-type">Type: ${instance.type}</span>`)
                .append(`<span class="instance-status">Status: ${instance.state}</span>`);

            instanceElem.click(function() {
                $('.instance-item', container).removeClass('selected');
                $(this).addClass('selected');
                selectedInstances['gcp-instances'] = instanceId;
                loadGCPInstanceMetrics(instanceId);
            });

            container.append(instanceElem);
        });

        if (Object.keys(instances).length > 0) {
            const firstInstanceId = Object.keys(instances)[0];
            $(`#gcp-instances .instance-item`).first().addClass('selected');
            selectedInstances['gcp-instances'] = firstInstanceId;
            loadGCPInstanceMetrics(firstInstanceId);
        }
    });
}

function loadAWS_EC2Metrics(instanceId) {
    $.get(`api//metrics/aws/ec2/${instanceId}`, function(data) {
        const cpuData = data.cpu_utilization;
        createTimeSeriesChart('aws-ec2-cpu-chart', `AWS EC2 ${instanceId} - CPU Utilization`, cpuData);

        if (data.memory_utilization && !data.memory_utilization.error) {
            createTimeSeriesChart('aws-ec2-memory-chart', `AWS EC2 ${instanceId} - Memory Utilization`, data.memory_utilization);
        } else {
            $('#aws-ec2-memory-chart').html('<div class="error-message">Memory metrics not available.</div>');
        }
    });
}

function loadAWS_RDSMetrics(instanceId) {
    $.get(`/api/metrics/aws/rds/${instanceId}`, function(data) {
        const cpuData = data.cpu_utilization;
        createTimeSeriesChart('aws-rds-cpu-chart', `AWS RDS ${instanceId} - CPU Utilization`, cpuData);

        const storageData = data.free_storage;
        createTimeSeriesChart('aws-rds-storage-chart', `AWS RDS ${instanceId} - Free Storage Space`, storageData, 
            { yaxis: { title: 'Bytes', tickformat: '.2s' } });
    });
}

function loadGCPInstanceMetrics(instanceId) {
    $.get(`/api/metrics/gcp/instances/${instanceId}`, function(data) {
        const cpuData = data.cpu_utilization;
        createTimeSeriesChart('gcp-instance-cpu-chart', `GCP Instance ${instanceId} - CPU Utilization`, cpuData);

        const diskData = data.disk_usage;
        createTimeSeriesChart('gcp-instance-disk-chart', `GCP Instance ${instanceId} - Disk Usage`, diskData, 
            { yaxis: { title: 'Bytes', tickformat: '.2s' } });
    });
}

function createTimeSeriesChart(elementId, title, metricData, additionalLayout = {}) {
    const timestamps = Object.keys(metricData.data_points).map(t => new Date(parseInt(t)));
    const values = Object.values(metricData.data_points);

    const trace = {
        x: timestamps,
        y: values,
        type: 'scatter',
        mode: 'lines+markers',
        name: metricData.metric,
        line: {
            color: '#ff9900',
            width: 2
        },
        marker: {
            size: 5,
            color: '#232f3e'
        }
    };

    const layout = {
        title: title,
        height: 300,
        margin: { l: 50, r: 20, t: 40, b: 50 },
        yaxis: {
            title: metricData.unit
        },
        xaxis: {
            title: 'Time'
        },
        ...additionalLayout
    };

    Plotly.newPlot(elementId, [trace], layout);
}
