// ---------------- GRADE MAP ----------------
const gradeMap = {
    "A+": 4.0, "A": 4.0, "A-": 3.7,
    "B+": 3.3, "B": 3.0, "B-": 2.7,
    "C+": 2.3, "C": 2.0,
    "D": 1.0,
    "F": 0.0
};

// ---------------- SUBJECT DATA ----------------
const subjects = subjectsData.map(s => ({
    name: s.subject_name,
    gp: gradeMap[s.grade] || 0
}));

// ---------------- OVERALL GPA ----------------
const totalPoints = subjects.reduce((sum, s) => sum + s.gp, 0);
const overallGpa = (totalPoints / subjects.length).toFixed(2);

document.getElementById("overallGpa").innerText = `GPA: ${overallGpa}`;

const gpaStatus = document.getElementById("gpaStatus");

if (overallGpa >= 3.0)
    gpaStatus.innerHTML = "✅ Excellent Performance";
else if (overallGpa >= 2.0)
    gpaStatus.innerHTML = "⚠️ Average – Needs Improvement";
else
    gpaStatus.innerHTML = "❌ Academic Risk";

// ---------------- SUBJECT CHART ----------------
new Chart(document.getElementById("subjectChart"), {
    type: "bar",
    data: {
        labels: subjects.map(s => s.name),
        datasets: [{
            label: "Grade Point",
            data: subjects.map(s => s.gp)
        }]
    }
});

// ---------------- TABLE + RISK ----------------
const subjectTable = document.getElementById("subjectTable");
const suggestionList = document.getElementById("suggestionList");

let riskCount = 0;

subjects.forEach(s => {
    let status = "Good";
    let cls = "good";

    if (s.gp < 2.0) {
        status = "Weak";
        cls = "risk";
        riskCount++;
        suggestionList.innerHTML += `<li>Improve ${s.name} with extra practice.</li>`;
    }

    subjectTable.innerHTML += `
        <tr>
            <td>${s.name}</td>
            <td>${s.gp.toFixed(1)}</td>
            <td class="${cls}">${status}</td>
        </tr>
    `;
});

// ---------------- RISK STATUS ----------------
document.getElementById("riskStatus").innerHTML =
    riskCount > 0
    ? `⚠️ You have ${riskCount} weak subject(s).`
    : `✅ No academic risk detected.`;
