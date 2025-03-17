import ApexCharts from 'apexcharts'

document.addEventListener("DOMContentLoaded", async function () {
    const activeFeedsCount = document.getElementById("activeFeeds")
    const activeFeedsCountRefresh = document.getElementById("activeFeedsRefresh")

    if (activeFeedsCount && activeFeedsCountRefresh) {
        const getData = async () => {
            const response = await fetch("/api/streams/active_sessions/")
            return await response.json()
        }
        const setData = async () => {
            const data = await getData()
            const {active_feeds} = data
            activeFeedsCount.innerText = active_feeds
        }

        setData()

        activeFeedsCountRefresh.onclick = () => setData()

    }


    const subscriptionPlanName = document.getElementById("subscriptionPlan")

    if (subscriptionPlanName) {

        const response = await fetch("/api/account/subscription/")
        if (response.status === 402) {
            subscriptionPlanName.innerText = "-"
        } else {
            const data = await response.json()
            subscriptionPlanName.innerText = data?.plan?.name
            const status = data?.subscription?.status
            const statusColor = status === "active" || status === "trialing" ? "badge-success" : "badge-danger"
            const statusElement = document.getElementById("subscriptionPlanStatus")
            statusElement.innerText = status
            statusElement.classList.add(statusColor)
        }

    }

    const streamTime = document.getElementById("streamTime")
    const avgStreamTime = document.getElementById("avgStreamTime")
    const chartStreamTimeTrend = document.getElementById("streamTimeChart")

    if (streamTime && avgStreamTime && chartStreamTimeTrend) {
        const response = await fetch("/api/streams/sessions_analytics/",)
        const data = await response.json()
        streamTime.innerText = data.total_stream_time + " hrs";
        avgStreamTime.innerText = data.average_stream_time;

        // Render Watch Time Chart
        new ApexCharts(chartStreamTimeTrend, {
            series: [{name: "Stream Time (hrs)", data: data.stream_time_series}],
            chart: {type: "line", height: 250, toolbar: {show: false}},
            xaxis: {categories: data.months},
            stroke: {curve: "smooth"},
            colors: ["#2196f3"],
        }).render();

    }

    const bandwidthUsed = document.getElementById("bandwidthUsed")
    const avgBandwidth = document.getElementById("avgBandwidth")
    const bandwidthLimit = document.getElementById("bandwidthLimit")


    if (bandwidthUsed && avgBandwidth && bandwidthLimit) {
        const response = await fetch("/api/streams/bandwidth_usage/",)
        const data = await response.json()


        bandwidthUsed.innerText = data.total_bandwidth + " GB";
        avgBandwidth.innerText = data.average_bandwidth;
        bandwidthLimit.innerText = data.bandwidth_limit ? data.bandwidth_limit + " GB" : "Unlimited";

        // Show alert if bandwidth exceeded
        if (data.alert) {
            let alertBox = document.getElementById("bandwidthAlert");
            alertBox.innerText = data.alert;
            alertBox.classList.remove("hidden");
        }

        // Render Bandwidth Chart
        new ApexCharts(document.querySelector("#bandwidthChart"), {
            series: [{name: "Bandwidth (GB)", data: data.bandwidth_series}],
            chart: {type: "bar", height: 250,toolbar:{show:false}},
            xaxis: {categories: data.months},
            colors: ["#EF4444"], // Tailwind Red
        }).render();
    }


})