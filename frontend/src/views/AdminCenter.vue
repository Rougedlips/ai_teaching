<template>
  <div class="page-container">
    <el-card shadow="never" class="main-card">
      <template #header>
        <div class="header-row">
          <div>
            <div class="title">管理员中心</div>
            <div class="subtitle">学期、教师、学生统一管理</div>
          </div>
          <el-tag type="danger">仅管理员可见</el-tag>
        </div>
      </template>

      <el-tabs v-model="activeTab">
        <el-tab-pane label="学期管理" name="semester">
          <div class="toolbar">
            <el-button type="primary" @click="openSemesterDialog()">新增学期</el-button>
          </div>
          <el-table :data="semesters" stripe>
            <el-table-column prop="name" label="学期名称" min-width="160" />
            <el-table-column prop="start_date" label="开始日期" width="130" />
            <el-table-column prop="end_date" label="结束日期" width="130" />
            <el-table-column label="启用" width="100">
              <template #default="scope">
                <el-tag :type="scope.row.is_enabled ? 'success' : 'info'">{{ scope.row.is_enabled ? '是' : '否' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="当前学期" width="100">
              <template #default="scope">
                <el-tag v-if="scope.row.is_current" type="warning">当前</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="240">
              <template #default="scope">
                <el-button link type="primary" @click="openSemesterDialog(scope.row)">编辑</el-button>
                <el-button link type="success" @click="setCurrentSemester(scope.row.id)">设为当前</el-button>
                <el-button link type="danger" @click="deleteSemester(scope.row.id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="老师账号管理" name="teacher">
          <div class="toolbar">
            <el-button type="primary" @click="openTeacherDialog()">新增老师</el-button>
            <el-upload :show-file-list="false" :http-request="uploadTeacherExcel" accept=".xlsx">
              <el-button type="success" plain>Excel导入</el-button>
            </el-upload>
            <el-button @click="downloadTeacherTemplate">下载导入模板</el-button>
          </div>

          <el-table :data="teachers" stripe>
            <el-table-column prop="username" label="账号" min-width="160" />
            <el-table-column prop="real_name" label="姓名" min-width="140" />
            <el-table-column label="管理员" width="100">
              <template #default="scope">
                <el-tag :type="scope.row.is_admin ? 'danger' : 'info'">{{ scope.row.is_admin ? '是' : '否' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180">
              <template #default="scope">
                <el-button link type="primary" @click="openTeacherDialog(scope.row)">编辑</el-button>
                <el-button link type="danger" @click="deleteTeacher(scope.row.id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="学生管理" name="student">
          <el-form inline class="filter-row">
            <el-form-item label="年级"><el-input v-model="studentFilters.grade" clearable /></el-form-item>
            <el-form-item label="班级">
              <el-select v-model="studentFilters.class_name" clearable filterable placeholder="全部班级" style="width: 180px">
                <el-option v-for="c in currentClasses" :key="c.id" :label="c.name" :value="c.name" />
              </el-select>
            </el-form-item>
            <el-form-item label="专业方向"><el-input v-model="studentFilters.major_direction" clearable placeholder="如：人工智能" /></el-form-item>
            <el-form-item label="账号"><el-input v-model="studentFilters.username" clearable /></el-form-item>
            <el-form-item label="学号"><el-input v-model="studentFilters.student_no" clearable /></el-form-item>
            <el-form-item label="姓名"><el-input v-model="studentFilters.real_name" clearable /></el-form-item>
            <el-form-item label="老师名"><el-input v-model="studentFilters.teacher_name" clearable /></el-form-item>
            <el-form-item>
              <el-button type="primary" @click="fetchStudents">筛选</el-button>
              <el-button @click="resetStudentFilter">重置</el-button>
            </el-form-item>
          </el-form>

          <div class="toolbar">
            <el-button type="primary" @click="openStudentDialog()">新增学生</el-button>
            <el-upload :show-file-list="false" :http-request="uploadStudentExcel" accept=".xlsx">
              <el-button type="success" plain>Excel导入</el-button>
            </el-upload>
            <el-button @click="downloadStudentTemplate">下载导入模板</el-button>
          </div>

          <div class="class-overview" v-if="currentClasses.length">
            <span class="class-overview-label">当前学期班级：</span>
            <el-tag v-for="c in currentClasses" :key="c.id" effect="plain" class="class-overview-tag">{{ c.name }}</el-tag>
          </div>

          <el-table :data="students" stripe>
            <el-table-column prop="grade" label="年级" width="90" />
            <el-table-column prop="semester" label="学期" min-width="130" />
            <el-table-column prop="class_name" label="班级" width="140" />
            <el-table-column prop="major_direction" label="专业方向" min-width="180" />
            <el-table-column prop="teacher_name" label="归属老师" width="130" />
            <el-table-column prop="username" label="账号" min-width="130" />
            <el-table-column prop="student_no" label="学号" min-width="130" />
            <el-table-column prop="real_name" label="姓名" min-width="100" />
            <el-table-column label="操作" width="240">
              <template #default="scope">
                <el-button link type="primary" @click="openStudentDialog(scope.row)">编辑</el-button>
                <el-button link type="warning" @click="resetPassword(scope.row.id)">改密码</el-button>
                <el-button link type="danger" @click="deleteStudent(scope.row.id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="班级管理" name="class">
          <el-form inline class="filter-row">
            <el-form-item label="学期">
              <el-select v-model="classFilters.semester_id" clearable placeholder="全部学期" style="width: 180px">
                <el-option v-for="s in semesters" :key="s.id" :label="s.name" :value="s.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="班级名称"><el-input v-model="classFilters.class_name" clearable /></el-form-item>
            <el-form-item label="老师名"><el-input v-model="classFilters.teacher_name" clearable /></el-form-item>
            <el-form-item>
              <el-button type="primary" @click="fetchClassRows">筛选</el-button>
              <el-button @click="resetClassFilter">重置</el-button>
            </el-form-item>
          </el-form>

          <div class="toolbar">
            <el-button type="primary" @click="openClassDialog()">新增班级</el-button>
            <el-upload :show-file-list="false" :http-request="uploadClassExcel" accept=".xlsx">
              <el-button type="success">Excel导入</el-button>
            </el-upload>
            <el-button @click="downloadClassTemplate">下载导入模板</el-button>
          </div>

          <el-table :data="classRows" stripe>
            <el-table-column prop="id" label="班级编号" width="100" />
            <el-table-column prop="semester" label="所属学期" min-width="150" />
            <el-table-column prop="name" label="班级名称" min-width="180" />
            <el-table-column prop="teacher_name" label="班级老师" min-width="140" />
            <el-table-column label="班级学生" min-width="320">
              <template #default="scope">
                <div class="student-tags">
                  <el-tag
                    v-for="stu in scope.row.students"
                    :key="stu.id"
                    effect="plain"
                    class="student-tag"
                  >
                    {{ stu.real_name || stu.username }}
                  </el-tag>
                  <span v-if="!scope.row.students?.length" class="empty-text">暂无学生</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="240">
              <template #default="scope">
                <el-button link type="primary" @click="openClassDialog(scope.row)">编辑</el-button>
                <el-button link type="success" @click="openClassStudentsDialog(scope.row)">分配学生</el-button>
                <el-button link type="danger" @click="deleteClass(scope.row.id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <el-dialog v-model="semesterDialogVisible" :title="semesterForm.id ? '编辑学期' : '新增学期'" width="520px">
      <el-form label-width="100px">
        <el-form-item label="学期名称"><el-input v-model="semesterForm.name" /></el-form-item>
        <el-form-item label="持续时间">
          <el-date-picker
            v-model="semesterRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="是否启用"><el-switch v-model="semesterForm.is_enabled" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="semesterDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveSemester">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="teacherDialogVisible" :title="teacherForm.id ? '编辑老师' : '新增老师'" width="520px">
      <el-form label-width="100px">
        <el-form-item label="账号"><el-input v-model="teacherForm.username" /></el-form-item>
        <el-form-item label="姓名"><el-input v-model="teacherForm.real_name" /></el-form-item>
        <el-form-item label="密码"><el-input v-model="teacherForm.password" type="password" show-password placeholder="编辑时可留空" /></el-form-item>
        <el-form-item label="设为管理员"><el-switch v-model="teacherForm.is_admin" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="teacherDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveTeacher">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="studentDialogVisible" :title="studentForm.id ? '编辑学生' : '新增学生'" width="560px">
      <el-form label-width="100px">
        <el-form-item label="账号"><el-input v-model="studentForm.username" /></el-form-item>
        <el-form-item label="学号"><el-input v-model="studentForm.student_no" /></el-form-item>
        <el-form-item label="姓名"><el-input v-model="studentForm.real_name" /></el-form-item>
        <el-form-item label="年级"><el-input v-model="studentForm.grade" /></el-form-item>
        <el-form-item label="班级"><el-input v-model="studentForm.class_name" /></el-form-item>
        <el-form-item label="专业方向"><el-input v-model="studentForm.major_direction" placeholder="默认：人工智能+复合型创新" /></el-form-item>
        <el-form-item label="归属老师">
          <el-select v-model="studentForm.teacher_id" placeholder="请选择老师" clearable style="width: 100%">
            <el-option v-for="t in teachers" :key="t.id" :label="teacherDisplayName(t)" :value="t.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="密码"><el-input v-model="studentForm.password" type="password" show-password placeholder="编辑时可留空" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="studentDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveStudent">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="classDialogVisible" :title="classForm.id ? '编辑班级' : '新增班级'" width="560px">
      <el-form label-width="100px">
        <el-form-item label="所属学期">
          <el-select v-model="classForm.semester_id" placeholder="请选择学期" style="width: 100%">
            <el-option v-for="s in semesters" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="班级名称">
          <el-input v-model="classForm.name" />
        </el-form-item>
        <el-form-item label="班级老师">
          <el-select v-model="classForm.teacher_id" placeholder="请选择老师" style="width: 100%">
            <el-option v-for="t in teachers" :key="t.id" :label="teacherDisplayName(t)" :value="t.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="classDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveClass">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="classStudentsDialogVisible" title="分配班级学生" width="680px">
      <el-form label-width="100px">
        <el-form-item label="班级">
          <el-input :model-value="classStudentsDialogName" disabled />
        </el-form-item>
        <el-form-item label="班级学生">
          <el-select v-model="classStudentIds" multiple filterable style="width: 100%" placeholder="可多选，支持一个学生加入多个班级">
            <el-option
              v-for="s in students"
              :key="s.id"
              :label="`${s.real_name || s.username}${s.student_no ? `（${s.student_no}）` : ''}`"
              :value="s.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="classStudentsDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveClassStudents">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { UploadRequestOptions } from 'element-plus'

interface SemesterItem {
  id: number
  name: string
  start_date: string | null
  end_date: string | null
  is_enabled: boolean
  is_current: boolean
}

interface TeacherItem {
  id: number
  username: string
  real_name: string | null
  is_admin: boolean
}

interface StudentItem {
  id: number
  class_id?: number | null
  semester?: string | null
  username: string
  student_no: string | null
  real_name: string | null
  grade: string | null
  class_name: string | null
  major_direction: string | null
  teacher_id: number | null
  teacher_name: string | null
}

interface ClassStudentSimple {
  id: number
  username: string
  real_name: string | null
  student_no: string | null
}

interface ClassItem {
  id: number
  name: string
  semester_id: number
  semester: string
  teacher_id: number
  teacher_name?: string | null
  student_ids?: number[]
  students?: ClassStudentSimple[]
}

const api = 'http://127.0.0.1:8000'
const activeTab = ref('semester')

const semesters = ref<SemesterItem[]>([])
const teachers = ref<TeacherItem[]>([])
const students = ref<StudentItem[]>([])
const currentClasses = ref<ClassItem[]>([])
const classRows = ref<ClassItem[]>([])

const semesterDialogVisible = ref(false)
const teacherDialogVisible = ref(false)
const studentDialogVisible = ref(false)
const classDialogVisible = ref(false)
const classStudentsDialogVisible = ref(false)

const semesterForm = reactive({ id: 0, name: '', start_date: '', end_date: '', is_enabled: true })
const semesterRange = ref<string[]>([])

const teacherForm = reactive({ id: 0, username: '', real_name: '', password: '', is_admin: false })

const studentForm = reactive({
  id: 0,
  username: '',
  student_no: '',
  real_name: '',
  grade: '',
  class_name: '',
  major_direction: '人工智能+复合型创新',
  teacher_id: undefined as number | undefined,
  password: '',
})

const studentFilters = reactive({ grade: '', class_name: '', major_direction: '', username: '', student_no: '', real_name: '', teacher_name: '' })
const classFilters = reactive({ semester_id: undefined as number | undefined, class_name: '', teacher_name: '' })
const classForm = reactive({ id: 0, semester_id: 0, name: '', teacher_id: 0 })
const classStudentsDialogId = ref(0)
const classStudentsDialogName = ref('')
const classStudentIds = ref<number[]>([])

const teacherDisplayName = (t: TeacherItem) => t.real_name ? `${t.real_name}（${t.username}）` : t.username

const fetchSemesters = async () => {
  const res = await axios.get(`${api}/semesters`)
  semesters.value = res.data || []
}

const fetchTeachers = async () => {
  const res = await axios.get(`${api}/admin/teachers`)
  teachers.value = res.data || []
}

const fetchStudents = async () => {
  const res = await axios.get(`${api}/admin/students`, { params: studentFilters })
  students.value = res.data || []
}

const fetchCurrentClasses = async () => {
  const res = await axios.get(`${api}/admin/classes/current`)
  currentClasses.value = res.data || []
}

const fetchClassRows = async () => {
  const params: Record<string, string | number> = {}
  if (classFilters.semester_id) params.semester_id = classFilters.semester_id
  if (classFilters.class_name.trim()) params.class_name = classFilters.class_name.trim()
  if (classFilters.teacher_name.trim()) params.teacher_name = classFilters.teacher_name.trim()

  const res = await axios.get(`${api}/admin/classes/manage`, { params })
  classRows.value = res.data || []
}

const fetchAll = async () => {
  try {
    await Promise.all([fetchSemesters(), fetchTeachers(), fetchStudents(), fetchCurrentClasses(), fetchClassRows()])
  } catch {
    ElMessage.error('管理员数据加载失败，请检查后端服务')
  }
}

fetchAll()

const openSemesterDialog = (row?: SemesterItem) => {
  if (row) {
    semesterForm.id = row.id
    semesterForm.name = row.name
    semesterForm.start_date = row.start_date || ''
    semesterForm.end_date = row.end_date || ''
    semesterForm.is_enabled = row.is_enabled
    semesterRange.value = [semesterForm.start_date, semesterForm.end_date].filter(Boolean)
  } else {
    semesterForm.id = 0
    semesterForm.name = ''
    semesterForm.start_date = ''
    semesterForm.end_date = ''
    semesterForm.is_enabled = true
    semesterRange.value = []
  }
  semesterDialogVisible.value = true
}

const saveSemester = async () => {
  semesterForm.start_date = semesterRange.value?.[0] || ''
  semesterForm.end_date = semesterRange.value?.[1] || ''
  const payload = {
    name: semesterForm.name,
    start_date: semesterForm.start_date || null,
    end_date: semesterForm.end_date || null,
    is_enabled: semesterForm.is_enabled,
    is_current: false,
  }

  if (semesterForm.id) {
    await axios.put(`${api}/admin/semesters/${semesterForm.id}`, payload)
  } else {
    await axios.post(`${api}/admin/semesters`, payload)
  }
  semesterDialogVisible.value = false
  ElMessage.success('学期保存成功')
  await Promise.all([fetchSemesters(), fetchClassRows()])
}

const setCurrentSemester = async (id: number) => {
  await axios.post(`${api}/admin/semesters/set-current`, { semester_id: id })
  ElMessage.success('已设置为当前学期')
  await Promise.all([fetchSemesters(), fetchCurrentClasses(), fetchClassRows(), fetchStudents()])
}

const deleteSemester = async (id: number) => {
  await ElMessageBox.confirm('确认删除该学期吗？', '提示', { type: 'warning' })
  await axios.delete(`${api}/admin/semesters/${id}`)
  ElMessage.success('删除成功')
  await Promise.all([fetchSemesters(), fetchCurrentClasses(), fetchClassRows()])
}

const openTeacherDialog = (row?: TeacherItem) => {
  if (row) {
    teacherForm.id = row.id
    teacherForm.username = row.username
    teacherForm.real_name = row.real_name || ''
    teacherForm.password = ''
    teacherForm.is_admin = row.is_admin
  } else {
    teacherForm.id = 0
    teacherForm.username = ''
    teacherForm.real_name = ''
    teacherForm.password = ''
    teacherForm.is_admin = false
  }
  teacherDialogVisible.value = true
}

const saveTeacher = async () => {
  if (!teacherForm.username) return ElMessage.warning('请输入账号')
  if (!teacherForm.id && !teacherForm.password) return ElMessage.warning('请输入密码')

  const payload = {
    username: teacherForm.username,
    real_name: teacherForm.real_name || null,
    password: teacherForm.password || undefined,
    is_admin: teacherForm.is_admin,
  }

  if (teacherForm.id) {
    await axios.put(`${api}/admin/teachers/${teacherForm.id}`, payload)
  } else {
    await axios.post(`${api}/admin/teachers`, payload)
  }
  teacherDialogVisible.value = false
  ElMessage.success('老师账号保存成功')
  await fetchTeachers()
}

const deleteTeacher = async (id: number) => {
  await ElMessageBox.confirm('确认删除该老师账号吗？', '提示', { type: 'warning' })
  await axios.delete(`${api}/admin/teachers/${id}`)
  ElMessage.success('删除成功')
  await Promise.all([fetchTeachers(), fetchClassRows()])
}

const openStudentDialog = (row?: StudentItem) => {
  if (row) {
    studentForm.id = row.id
    studentForm.username = row.username
    studentForm.student_no = row.student_no || ''
    studentForm.real_name = row.real_name || ''
    studentForm.grade = row.grade || ''
    studentForm.class_name = row.class_name || ''
    studentForm.major_direction = row.major_direction || '人工智能+复合型创新'
    studentForm.teacher_id = row.teacher_id || undefined
    studentForm.password = ''
  } else {
    studentForm.id = 0
    studentForm.username = ''
    studentForm.student_no = ''
    studentForm.real_name = ''
    studentForm.grade = ''
    studentForm.class_name = ''
    studentForm.major_direction = '人工智能+复合型创新'
    studentForm.teacher_id = undefined
    studentForm.password = ''
  }
  studentDialogVisible.value = true
}

const saveStudent = async () => {
  const username = studentForm.username.trim()
  const password = studentForm.password.trim()

  if (!username) return ElMessage.warning('请输入账号')
  if (!studentForm.id && !password) return ElMessage.warning('请输入密码')

  const payload = {
    username,
    student_no: studentForm.student_no.trim() || null,
    real_name: studentForm.real_name.trim() || null,
    grade: studentForm.grade.trim() || null,
    class_name: studentForm.class_name.trim() || null,
    major_direction: studentForm.major_direction.trim() || '人工智能+复合型创新',
    teacher_id: studentForm.teacher_id || null,
    password: password || undefined,
  }

  try {
    if (studentForm.id) {
      await axios.put(`${api}/admin/students/${studentForm.id}`, payload)
    } else {
      await axios.post(`${api}/admin/students`, payload)
    }
    studentDialogVisible.value = false
    ElMessage.success('学生账号保存成功')
    await fetchStudents()
  } catch (e: any) {
    const detail = e?.response?.data?.detail || '保存失败，请检查账号、学号是否重复'
    ElMessage.error(String(detail))
  }
}

const deleteStudent = async (id: number) => {
  await ElMessageBox.confirm('确认删除该学生账号吗？', '提示', { type: 'warning' })
  await axios.delete(`${api}/admin/students/${id}`)
  ElMessage.success('删除成功')
  await Promise.all([fetchStudents(), fetchClassRows()])
}

const resetPassword = async (id: number) => {
  const { value } = await ElMessageBox.prompt('请输入新密码', '重置密码', {
    inputType: 'password',
    confirmButtonText: '确认',
    cancelButtonText: '取消',
  })
  const pwd = String(value || '').trim()
  if (!pwd) return

  await axios.put(`${api}/admin/students/${id}/password`, { new_password: pwd })
  ElMessage.success('密码修改成功')
}

const resetStudentFilter = () => {
  studentFilters.grade = ''
  studentFilters.class_name = ''
  studentFilters.major_direction = ''
  studentFilters.username = ''
  studentFilters.student_no = ''
  studentFilters.real_name = ''
  studentFilters.teacher_name = ''
  fetchStudents()
}

const resetClassFilter = () => {
  classFilters.semester_id = undefined
  classFilters.class_name = ''
  classFilters.teacher_name = ''
  fetchClassRows()
}

const openClassDialog = (row?: ClassItem) => {
  if (row) {
    classForm.id = row.id
    classForm.semester_id = row.semester_id
    classForm.name = row.name
    classForm.teacher_id = row.teacher_id
  } else {
    classForm.id = 0
    classForm.semester_id = semesters.value.find((s) => s.is_current)?.id || semesters.value[0]?.id || 0
    classForm.name = ''
    classForm.teacher_id = teachers.value[0]?.id || 0
  }
  classDialogVisible.value = true
}

const saveClass = async () => {
  if (!classForm.semester_id) return ElMessage.warning('请选择所属学期')
  if (!classForm.name.trim()) return ElMessage.warning('请输入班级名称')
  if (!classForm.teacher_id) return ElMessage.warning('请选择班级老师')

  if (classForm.id) {
    await axios.put(`${api}/admin/classes/${classForm.id}`, {
      semester_id: classForm.semester_id,
      name: classForm.name,
      teacher_id: classForm.teacher_id,
    })
  } else {
    await axios.post(`${api}/admin/classes`, {
      semester_id: classForm.semester_id,
      name: classForm.name,
      teacher_id: classForm.teacher_id,
    })
  }

  classDialogVisible.value = false
  ElMessage.success('班级保存成功')
  await Promise.all([fetchCurrentClasses(), fetchClassRows()])
}

const openClassStudentsDialog = (row: ClassItem) => {
  classStudentsDialogId.value = row.id
  classStudentsDialogName.value = row.name
  classStudentIds.value = row.student_ids || []
  classStudentsDialogVisible.value = true
}

const saveClassStudents = async () => {
  if (!classStudentsDialogId.value) return
  await axios.post(`${api}/admin/classes/${classStudentsDialogId.value}/students`, {
    student_ids: classStudentIds.value
  })
  classStudentsDialogVisible.value = false
  ElMessage.success('班级学生已更新')
  await Promise.all([fetchStudents(), fetchClassRows()])
}

const deleteClass = async (id: number) => {
  await ElMessageBox.confirm('确认删除该班级吗？', '提示', { type: 'warning' })
  await axios.delete(`${api}/admin/classes/${id}`)
  ElMessage.success('班级已删除')
  await Promise.all([fetchCurrentClasses(), fetchClassRows()])
}

const downloadTemplate = async (url: string, fallbackFileName: string) => {
  try {
    const res = await axios.get(url, { responseType: 'blob' })
    const contentType = String(res.headers?.['content-type'] || '')

    if (contentType.includes('application/json')) {
      const text = await res.data.text()
      try {
        const json = JSON.parse(text)
        ElMessage.error(json?.detail || '模板下载失败')
      } catch {
        ElMessage.error('模板下载失败')
      }
      return
    }

    const disposition = String(res.headers?.['content-disposition'] || '')
    const matched = disposition.match(/filename\*=UTF-8''([^;]+)|filename="?([^";]+)"?/i)
    const fileName = decodeURIComponent(matched?.[1] || matched?.[2] || fallbackFileName)

    const blobUrl = URL.createObjectURL(res.data)
    const a = document.createElement('a')
    a.href = blobUrl
    a.download = fileName
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(blobUrl)
  } catch (e: any) {
    try {
      const errData = e?.response?.data
      if (errData instanceof Blob) {
        const text = await errData.text()
        const json = JSON.parse(text)
        ElMessage.error(json?.detail || '模板下载失败')
        return
      }
      ElMessage.error(e?.response?.data?.detail || '模板下载失败')
    } catch {
      ElMessage.error('模板下载失败')
    }
  }
}

const downloadTeacherTemplate = () => downloadTemplate(`${api}/admin/templates/teachers`, 'teachers_template.xlsx')

const downloadStudentTemplate = () => downloadTemplate(`${api}/admin/templates/students`, 'students_template.xlsx')

const downloadClassTemplate = () => downloadTemplate(`${api}/admin/templates/classes`, 'classes_template.xlsx')

const uploadTeacherExcel = async (options: UploadRequestOptions) => {
  try {
    const formData = new FormData()
    formData.append('file', options.file)
    const res = await axios.post(`${api}/admin/teachers/import`, formData)
    ElMessage.success(`导入完成：新增 ${res.data.created} 条，跳过 ${res.data.skipped} 条`)
    options.onSuccess?.(res.data)
    await fetchTeachers()
  } catch (e: any) {
    const detail = e?.response?.data?.detail || '老师Excel导入失败'
    ElMessage.error(String(detail))
    options.onError?.(e)
  }
}

const uploadStudentExcel = async (options: UploadRequestOptions) => {
  try {
    const formData = new FormData()
    formData.append('file', options.file)
    const res = await axios.post(`${api}/admin/students/import`, formData)
    ElMessage.success(`导入完成：新增 ${res.data.created} 条，跳过 ${res.data.skipped} 条`)
    options.onSuccess?.(res.data)
    await Promise.all([fetchStudents(), fetchClassRows()])
  } catch (e: any) {
    const detail = e?.response?.data?.detail || '学生Excel导入失败'
    ElMessage.error(String(detail))
    options.onError?.(e)
  }
}

const uploadClassExcel = async (options: UploadRequestOptions) => {
  try {
    const formData = new FormData()
    formData.append('file', options.file)
    const res = await axios.post(`${api}/admin/classes/import`, formData)
    ElMessage.success(`导入完成：新增 ${res.data.created} 条，跳过 ${res.data.skipped} 条`)
    options.onSuccess?.(res.data)
    await Promise.all([fetchCurrentClasses(), fetchClassRows()])
  } catch (e: any) {
    const detail = e?.response?.data?.detail || '班级Excel导入失败'
    ElMessage.error(String(detail))
    options.onError?.(e)
  }
}
</script>

<style scoped>
.page-container { padding: 0; }
.main-card { border-radius: 10px; border: 1px solid #eceffc; }
.header-row { display: flex; justify-content: space-between; align-items: center; }
.title { font-size: 18px; font-weight: 700; color: #28334a; }
.subtitle { margin-top: 4px; color: #8590a6; font-size: 12px; }
.toolbar { display: flex; gap: 10px; margin-bottom: 12px; }
.filter-row { margin-bottom: 8px; background: #f7f9ff; padding: 10px 10px 0; border-radius: 8px; }
.class-overview { margin: 0 0 12px; display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
.class-overview-label { color: #606266; font-size: 13px; }
.class-overview-tag { max-width: 360px; white-space: normal; height: auto; line-height: 1.3; }
.student-tags { display: flex; flex-wrap: wrap; gap: 6px; }
.student-tag { max-width: 130px; overflow: hidden; text-overflow: ellipsis; }
.empty-text { color: #909399; font-size: 12px; }
</style>
