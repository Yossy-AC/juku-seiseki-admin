// ===== ダッシュボードのメインロジック =====

// ページ読み込み時の処理
document.addEventListener('DOMContentLoaded', async () => {
    try {
        console.log('Dashboard loading...');

        // データ読み込む
        const loaded = await dataLoader.loadAllData();
        console.log('Data loaded:', loaded);

        if (!loaded) {
            const msg = 'データ読み込みエラーが発生しました';
            console.error(msg);
            alert(msg);
            return;
        }

        console.log('Students:', dataLoader.students);
        console.log('Grades:', dataLoader.grades);

        // URLパラメータから生徒IDを取得（デモ用は最初の生徒を表示）
        const urlParams = new URLSearchParams(window.location.search);
        const studentId = urlParams.get('studentId') || dataLoader.students[0]?.id;

        console.log('StudentId:', studentId);

        if (!studentId) {
            alert('生徒が見つかりません');
            return;
        }

        // ダッシュボードを表示
        displayDashboard(studentId);
    } catch (error) {
        console.error('Unexpected error:', error);
        alert(`予期しないエラー: ${error.message}`);
    }
});

// ダッシュボード表示関数
function displayDashboard(studentId) {
    const student = dataLoader.getStudent(studentId);
    
    if (!student) {
        alert(`生徒ID ${studentId} が見つかりません`);
        return;
    }

    // 講座をjsonから取得、なければデフォルト値
    let classInfo = dataLoader.getClass(student.classId);
    if (!classInfo) {
        classInfo = { name: student.classroom || '不明' };
    }

    const grades = dataLoader.getStudentGrades(studentId);
    const attendance = dataLoader.getStudentAttendance(studentId);

    if (grades.length === 0) {
        console.warn('No grades found for student:', studentId);
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

    if (grades.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: #999;">成績がまだありません</td></tr>';
        return;
    }

    grades.forEach(grade => {
        let scorePercentage, classAverage, difference, diffClass, diffSign;

        // 新フォーマット（scores.totalが存在）
        if (grade.scores && grade.scores.total !== undefined) {
            scorePercentage = Math.round((grade.scores.total / grade.maxScores.total) * 100);
        } else {
            // 従来のフォーマット
            scorePercentage = Math.round((grade.score / grade.maxScore) * 100);
        }

        classAverage = dataLoader.calculateClassAverage(
            dataLoader.getStudent(studentId).classId,
            grade.date
        );
        difference = scorePercentage - classAverage;
        diffClass = difference >= 0 ? 'positive' : 'negative';
        diffSign = difference >= 0 ? '+' : '';

        // 表示する成績を取得
        const displayScore = grade.scores && grade.scores.total !== undefined 
            ? `${grade.scores.total}/${grade.maxScores.total}`
            : `${grade.score}/${grade.maxScore}`;

        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${new Date(grade.date).toLocaleDateString('ja-JP')}</td>
            <td>${displayScore}</td>
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
    const recentScores = recentGrades.map(g => {
        if (g.scores && g.scores.total !== undefined) {
            return g.scores.total / g.maxScores.total * 100;
        } else {
            return g.score / g.maxScore * 100;
        }
    });
    const recentAverage = recentScores.reduce((a, b) => a + b, 0) / recentScores.length;

    const prevGrades = grades.slice(0, -3);
    const prevScores = prevGrades.map(g => {
        if (g.scores && g.scores.total !== undefined) {
            return g.scores.total / g.maxScores.total * 100;
        } else {
            return g.score / g.maxScore * 100;
        }
    });
    const prevAverage = prevScores.length > 0 ? prevScores.reduce((a, b) => a + b, 0) / prevScores.length : recentAverage;

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
