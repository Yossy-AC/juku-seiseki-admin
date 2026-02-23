// ===== データ読み込む関数 =====
class DataLoader {
    constructor() {
        this.classes = [];
        this.students = [];
        this.grades = [];
        this.attendance = [];
    }

    // JSONファイルを取得
    async loadJSON(path) {
        try {
            console.log(`Loading: ${path}`);
            const response = await fetch(path);
            if (!response.ok) {
                const error = `Failed to load ${path}: ${response.statusText}`;
                console.error(error);
                alert(error);
                throw new Error(error);
            }
            const data = await response.json();
            console.log(`Loaded ${path}:`, data);
            return data;
        } catch (error) {
            console.error(`Error loading ${path}:`, error);
            alert(`データ読み込みエラー: ${path}\n${error.message}`);
            return null;
        }
    }

    // すべてのデータを読み込む
    async loadAllData() {
        try {
            // 相対パスを使用してJSONファイルを読み込む
            const classesData = await this.loadJSON('../data/classes.json');
            const studentsData = await this.loadJSON('../data/students.json');
            const gradesData = await this.loadJSON('../data/grades.json');
            const attendanceData = await this.loadJSON('../data/attendance.json');

            if (classesData) this.classes = classesData.classes || [];
            if (studentsData) this.students = studentsData.students || [];
            if (gradesData) {
                this.grades = gradesData.grades || [];
                this.mockExams = gradesData.mockExams || [];
            }
            if (attendanceData) this.attendance = attendanceData.attendance || [];

            console.log('All data loaded successfully');
            return true;
        } catch (error) {
            console.error('Error loading all data:', error);
            return false;
        }
    }

    // 生徒情報を取得
    getStudent(studentId) {
        return this.students.find(s => s.id === studentId);
    }

    // 講座情報を取得
    getClass(classId) {
        return this.classes.find(c => c.id === classId);
    }

    // 特定の生徒の成績を取得
    getStudentGrades(studentId) {
        return this.grades.filter(g => g.studentId === studentId)
            .sort((a, b) => new Date(a.date) - new Date(b.date));
    }

    // 特定の生徒の出席記録を取得
    getStudentAttendance(studentId) {
        return this.attendance.filter(a => a.studentId === studentId)
            .sort((a, b) => new Date(a.date) - new Date(b.date));
    }

    // 講座のすべての成績を取得
    getClassGrades(classId) {
        return this.grades.filter(g => {
            const student = this.students.find(s => s.id === g.studentId);
            return student && student.classId === classId;
        });
    }

    // クラス平均を計算
    calculateClassAverage(classId, date = null) {
        const classGrades = this.getClassGrades(classId);
        let relevantGrades = classGrades;

        // 特定の日付の成績に絞る場合
        if (date) {
            relevantGrades = classGrades.filter(g => g.date === date);
        }

        if (relevantGrades.length === 0) return 0;

        const total = relevantGrades.reduce((sum, g) => {
            return sum + (g.score / g.maxScore * 100);
        }, 0);

        return Math.round(total / relevantGrades.length);
    }

    // 特定の生徒の平均を計算
    calculateStudentAverage(studentId) {
        const studentGrades = this.getStudentGrades(studentId);
        if (studentGrades.length === 0) return 0;

        const total = studentGrades.reduce((sum, g) => {
            return sum + (g.score / g.maxScore * 100);
        }, 0);

        return Math.round(total / studentGrades.length);
    }

    // 出席率を計算
    calculateAttendanceRate(studentId) {
        const records = this.getStudentAttendance(studentId);
        if (records.length === 0) return 0;

        const present = records.filter(a => a.status === '出席').length;
        return Math.round((present / records.length) * 100);
    }
}

// グローバルインスタンス
const dataLoader = new DataLoader();
