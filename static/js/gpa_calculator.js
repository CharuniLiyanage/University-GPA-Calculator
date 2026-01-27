let subjects = [];

function addSubject(){
    const subject = document.getElementById('subject').value.trim();
    const credits = parseFloat(document.getElementById('credits').value);
    const grade = parseFloat(document.getElementById('grade').value);

    if(!subject || !credits || isNaN(grade)){
        alert("Please fill all fields correctly!");
        return;
    }

    subjects.push({subject, credits, grade});
    document.getElementById('gpaForm').reset();
    renderTable();
    calculateGPA();
}

function removeSubject(index){
    subjects.splice(index, 1);
    renderTable();
    calculateGPA();
}

function renderTable(){
    const tbody = document.getElementById('subjectTable').querySelector('tbody');
    tbody.innerHTML = "";
    subjects.forEach((sub, i) => {
        tbody.innerHTML += `<tr>
            <td>${sub.subject}</td>
            <td>${sub.credits}</td>
            <td>${sub.grade}</td>
            <td><button onclick="removeSubject(${i})">Remove</button></td>
        </tr>`;
    });
}

function calculateGPA(){
    let totalCredits = 0;
    let totalPoints = 0;

    subjects.forEach(sub => {
        totalCredits += sub.credits;
        totalPoints += sub.credits * sub.grade;
    });

    const gpa = totalCredits ? (totalPoints / totalCredits).toFixed(2) : 0.00;
    document.getElementById('gpaValue').textContent = `GPA: ${gpa}`;
}
