// ===== 講師管理画面のロジック =====

document.addEventListener('DOMContentLoaded', async () => {
    console.log('Admin page loading...');

    // データ読み込む
    const loaded = await dataLoader.loadAllData();
    if (!loaded) {
        alert('データ読み込みエラーが発生しました');
        return;
    }

    // UI初期化
    initializeUI();
    displayDashboard();
    populateClassSelects();
    displayStudents();
    displayClasses();
    displayRecentGrades();

    // イベントリスナー設定
    setupEventListeners();
});

// UI初期化
function initializeUI() {
    // タブ切り替え
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const tabName = btn.dataset.tab;
            switchTab(tabName);
        });
    });

    // 講座選択時に生徒を更新
    document.getElementById('classSelect').addEventListener('change', (e) => {
        updateStudentSelect(e.target.value);
    });

    // 成績入力フォーム送信
    document.getElementById('gradesForm').addEventListener('submit', (e) => {
        e.preventDefault();
        handleGradesSubmit();
    });

    // 今日の日付をデフォルトに
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('testDate').value = today;
}

// タブ切り替え
function switchTab(tabName) {
    // すべてのタブコンテンツを非表示
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });

    // すべてのボタンをアクティブ解除
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // 指定したタブを表示
    document.getElementById(tabName).classList.add('active');
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
}

// ダッシュボード表示
function displayDashboard() {
    const summary = document.getElementById('classSummary');
    summary.innerHTML = '';

    dataLoader.classes.forEach(classInfo => {
        const students = dataLoader.students.filter(s => s.classId === classInfo.id);
        const card = document.createElement('div');
        card.className = 'summary-card';
        card.innerHTML = `
            <h3>${classInfo.name}</h3>
            <p>${classInfo.day} ${classInfo.time}</p>
            <p class="number">${students.length}/${classInfo.capacity}</p>
            <p>${Math.round((students.length / classInfo.capacity) * 100)}%</p>
        `;
        summary.appendChild(card);
    });
}

// 講座セレクトボックスを填充
function populateClassSelects() {
    const classSelect = document.getElementById('classSelect');
    const reportClassSelect = document.getElementById('reportClassSelect');

    dataLoader.classes.forEach(classInfo => {
        const option1 = document.createElement('option');
        option1.value = classInfo.id;
        option1.textContent = classInfo.name;
        classSelect.appendChild(option1);

        const option2 = document.createElement('option');
        option2.value = classInfo.id;
        option2.textContent = classInfo.name;
        reportClassSelect.appendChild(option2);
    });
}

// 生徒セレクトボックスを更新
function updateStudentSelect(classId) {
    const studentSelect = document.getElementById('studentSelect');
    studentSelect.innerHTML = '<option value="">生徒を選択してください</option>';

    if (!classId) return;

    const students = dataLoader.students.filter(s => s.classId === classId);
    students.forEach(student => {
        const option = document.createElement('option');
        option.value = student.id;
        option.textContent = student.name;
        studentSelect.appendChild(option);
    });
}

// 生徒一覧を表示
function displayStudents() {
    const tbody = document.getElementById('studentsTable');
    tbody.innerHTML = '';

    dataLoader.students.forEach(student => {
        const classInfo = dataLoader.getClass(student.classId);
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${student.id}</td>
            <td>${student.name}</td>
            <td>${classInfo.name}</td>
            <td>${new Date(student.joinDate).toLocaleDateString('ja-JP')}</td>
            <td>
                <button class="btn btn-primary" onclick="viewStudent('${student.id}')">詳細</button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// 講座一覧を表示
function displayClasses() {
    const tbody = document.getElementById('classesTable');
    tbody.innerHTML = '';

    dataLoader.classes.forEach(classInfo => {
        const students = dataLoader.students.filter(s => s.classId === classInfo.id);
        const rate = Math.round((students.length / classInfo.capacity) * 100);
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${classInfo.name}</td>
            <td>${classInfo.day} ${classInfo.time}</td>
            <td>${classInfo.capacity}</td>
            <td>${students.length}</td>
            <td>${rate}%</td>
        `;
        tbody.appendChild(row);
    });
}

// 最近の成績を表示
function displayRecentGrades() {
    const tbody = document.getElementById('recentGradesTable');
    tbody.innerHTML = '';

    // ローカルストレージから取得
    const grades = JSON.parse(localStorage.getItem('gradeData')) || dataLoader.grades;

    // 最新20件を逆順で表示
    const recent = grades.slice(-20).reverse();
    recent.forEach(grade => {
        const student = dataLoader.getStudent(grade.studentId);
        if (!student) return;

        const classInfo = dataLoader.getClass(grade.classId);
        
        // 新フォーマットと従来フォーマットに対応
        let displayScore, rate;
        if (grade.scores && grade.scores.total !== undefined) {
            displayScore = `${grade.scores.total}/${grade.maxScores.total}`;
            rate = Math.round((grade.scores.total / grade.maxScores.total) * 100);
        } else {
            displayScore = `${grade.score}/${grade.maxScore}`;
            rate = Math.round((grade.score / grade.maxScore) * 100);
        }

        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${new Date(grade.date).toLocaleDateString('ja-JP')}</td>
            <td>${student.name}</td>
            <td>${classInfo.name}</td>
            <td>${displayScore}</td>
            <td>${rate}%</td>
        `;
        tbody.appendChild(row);
    });
}

// 成績入力フォーム処理
function handleGradesSubmit() {
    const classId = document.getElementById('classSelect').value;
    const studentId = document.getElementById('studentSelect').value;
    const date = document.getElementById('testDate').value;
    const score = parseInt(document.getElementById('score').value);
    const maxScore = parseInt(document.getElementById('maxScore').value);
    const testName = document.getElementById('testName').value;

    if (!classId || !studentId || !date || !score || !maxScore || !testName) {
        alert('すべてのフィールドを入力してください');
        return;
    }

    if (score > maxScore) {
        alert('点数が満点を超えています');
        return;
    }

    // ローカルストレージから取得（新フォーマットにも対応）
    const grades = JSON.parse(localStorage.getItem('gradeData')) || [];

    // 新規成績を追加（新フォーマット対応）
    const newGrade = {
        id: `g${Date.now()}`,
        studentId: studentId,
        classId: classId,
        date: date,
        lessonNumber: grades.filter(g => g.studentId === studentId).length + 1,
        lessonContent: testName,
        scores: {
            comprehension: 0,
            unseenProblems: 0,
            grammar: 0,
            vocabulary: 0,
            listening: 0,
            total: score
        },
        maxScores: {
            comprehension: maxScore / 5,
            unseenProblems: maxScore / 5,
            grammar: maxScore / 5,
            vocabulary: maxScore / 5,
            listening: maxScore / 5,
            total: maxScore
        }
    };

    grades.push(newGrade);
    localStorage.setItem('gradeData', JSON.stringify(grades));

    alert('成績を追加しました（現在はデモ表示です。実装後はGitHubに保存されます）');

    // フォームリセット
    document.getElementById('gradesForm').reset();
    document.getElementById('testDate').value = new Date().toISOString().split('T')[0];

    // 一覧更新
    displayRecentGrades();
}

// イベントリスナー設定
function setupEventListeners() {
    // 必要に応じて追加
}

// 生徒詳細を表示（デモ用）
function viewStudent(studentId) {
    alert(`生徒 ${dataLoader.getStudent(studentId).name} の詳細表示は準備中です`);
}
