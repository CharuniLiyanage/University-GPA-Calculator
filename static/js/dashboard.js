// Grade to Point Mapping
const gradeMap = {
    "A+": 4.0, "A": 4.0, "A-": 3.7, "B+": 3.3, "B": 3.0, 
    "B-": 2.7, "C+": 2.3, "C": 2.0, "D": 1.0, "F": 0.0
};

// Check if data exists
if (window.subjectsData && subjectsData.length > 0) {
    const labels = subjectsData.map(s => s.subject_name);
    const values = subjectsData.map(s => gradeMap[s.grade] ?? 0);

    const ctx = document.getElementById("subjectChart").getContext("2d");
    new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "Grade Points",
                data: values,
                backgroundColor: "rgba(8, 64, 102, 0.7)",
                borderColor: "rgba(54, 162, 235, 1)",
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: { beginAtZero: true, max: 4 }
            }
        }
    });
} else {
    console.log("No subjects to display in chart.");
}