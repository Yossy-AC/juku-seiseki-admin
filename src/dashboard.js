// ===== ダッシュボードのメインロジック =====

// ページ読み込み時の処理
document.addEventListener('DOMContentLoaded', async () => {
    console.log('Dashboard loading...');

    // データ読み込む
    const loaded = await dataLoader.loadAllData();
    if (!loaded) {
        alert('データ読み込みエラーが発生しました');
        return;
    }

    // URLパラメータから生徒IDを取得（デモ用は最初の生徒を表示）
    const urlParams = new URLSearchParams(window.location.search);
    const studentId = urlParams.get('studentId') || dataLoader.students[0]?.id;

    if (!studentId) {
        alert('生徒が見つかりません');
        return;
    }

    // ダッシュボードを表示
    displayDashboard(studentId);
});

// ダッシュボード表示関数
function displayDashboard(studentId) {
    const student = dataLoader.getStudent(studentId);
    const classInfo = dataLoader.getClass(student.classId);
    const grades = dataLoader.getStudentGrades(studentId);
    const attendance = dataLoader.getStudentAttendance(studentId);

    if (!student || grades.length === 0) {
        alert('生徒情報または成績が見つかりません');
        return;
    }

    // === 生徒情報の表示 ===
    document.getElementById('studentName').textContent = student.name;
    document.getElementById('className').textContent = classInfo.name;

    // === 成績表の表示 ===
    displayGradesTable(studentId, grades);

    // === クラス平均との比較 ===
    displayComparison(studentId, student.classId);

    // === AIアドバイスの生成 ===
    displayAdvice(studentId, grades);

    // === 出席状況の表示 ===
    displayAttendance(studentId, attendance);
}

// 成績表の表示
function displayGradesTable(studentId, grades) {
    const tbody = document.getElementById('gradesTableBody');
    tbody.innerHTML = '';

    grades.forEach(grade => {
        const scorePercentage = Math.round((grade.score / grade.maxScore) * 100);
        const classAverage = dataLoader.calculateClassAverage(
            dataLoader.getStudent(studentId).classId,
            grade.date
        );
        const difference = scorePercentage - classAverage;
        const diffClass = difference >= 0 ? 'positive' : 'negative';
        const diffSign = difference >= 0 ? '+' : '';

        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${new Date(grade.date).toLocaleDateString('ja-JP')}</td>
            <td>${grade.score}/${grade.maxScore}</td>
            <td>${scorePercentage}%</td>
            <td>${classAverage}%</td>
            <td class="${diffClass}">${diffSign}${difference}%</td>
        `;
        tbody.appendChild(row);
    });
}

// クラス平均との比較表示
function displayComparison(studentId, classId) {
    const studentAverage = dataLoader.calculateStudentAverage(studentId);
    const classAverage = dataLoader.calculateClassAverage(classId);
    const difference = studentAverage - classAverage;
    const diffClass = difference >= 0 ? 'positive' : 'negative';
    const diffSign = difference >= 0 ? '+' : '';

    document.getElementById('myAverage').textContent = studentAverage;
    document.getElementById('classAverage').textContent = classAverage;

    const diffElement = document.getElementById('difference');
    diffElement.textContent = `${diffSign}${difference}%`;
    diffElement.className = `difference ${diffClass}`;
}

// AIアドバイスの生成
function displayAdvice(studentId, grades) {
    if (grades.length < 2) {
        document.getElementById('aiAdvice').textContent = 'まだアドバイスを生成するのに十分なデータがありません。';
        return;
    }

    const recentGrades = grades.slice(-3); // 最新3件
    const recentAverage = recentGrades.reduce((sum, g) => sum + (g.score / g.maxScore * 100), 0) / recentGrades.length;
    const prevAverage = grades.slice(0, -3).reduce((sum, g) => sum + (g.score / g.maxScore * 100), 0) / (grades.length - 3);

    let advice = '';

    if (recentAverage > prevAverage + 5) {
        advice = `🎉 素晴らしい！最近の成績が上がっています。この調子を保ってください。`;
    } else if (recentAverage < prevAverage - 5) {
        advice = `⚠️ 最近成績が低下しています。得点の低かった問題を復習することをお勧めします。`;
    } else {
        advice = `📚 成績が安定しています。新しい範囲の問題に挑戦してみてください。`;
    }

    // スコア別アドバイス
    const latestScore = recentAverage;
    if (latestScore < 60) {
        advice += ' 文法や単語の基礎から復習をお勧めします。';
    } else if (latestScore < 75) {
        advice += ' 長文読解の練習を増やしましょう。';
    } else if (latestScore < 90) {
        advice += ' 過去問を使った実践的な練習を心がけましょう。';
    } else {
        advice += ' 高いレベルを保つため、難関問題に挑戦してください。';
    }

    document.getElementById('aiAdvice').textContent = advice;
}

// 出席状況の表示
function displayAttendance(studentId, attendance) {
    const present = attendance.filter(a => a.status === '出席').length;
    const absent = attendance.filter(a => a.status === '欠席').length;
    const late = attendance.filter(a => a.status === '遅刻').length;
    const rate = dataLoader.calculateAttendanceRate(studentId);

    document.getElementById('attendanceRate').textContent = rate;
    document.getElementById('attendancePresent').textContent = present;
    document.getElementById('attendanceAbsent').textContent = absent;
    document.getElementById('attendanceLate').textContent = late;
}
