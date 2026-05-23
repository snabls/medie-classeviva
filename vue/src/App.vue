<template>
  <div class="container">
    <h1 class="main-title">ClasseViva Medie App</h1>

    <!-- SCHERMATA DI LOGIN -->
    <div v-if="!isLoggedIn" class="login-box">
      <h2>Accedi</h2>
      <input v-model="username" placeholder="Username (es. S1234567) o Email" class="input-field" />
      <input v-model="password" type="password" placeholder="Password" class="input-field" @keyup.enter="login" />
      <button @click="login" class="btn-primary">Calcola Medie</button>
      <p v-if="error" class="error-msg">{{ error }}</p>
    </div>

    <!-- DASHBOARD MEDIE -->
    <div v-else class="dashboard">
      <div class="general-average-card">
        <h2>Media Generale: <span :style="{ color: getColor(generalAverage) }">{{ generalAverage.toFixed(2) }}</span></h2>
      </div>

      <div class="subjects-grid">
        <div v-for="(subj, subjName) in subjectsData" :key="subjName" class="subject-card">
          <div class="subject-header">
            <h3>{{ subjName }}</h3>
            <h3 :style="{ color: getColor(subj.average) }">{{ subj.average.toFixed(2) }}</h3>
          </div>
          
          <ul class="grades-list">
            <li v-for="grade in subj.grades" :key="grade.id" class="grade-item">
              <div class="grade-info">
                <span class="grade-value" :style="{ color: getColor(grade.value) }">{{ grade.display }}</span>
                <span class="grade-date">{{ grade.date }}</span>
              </div>
              
              <!-- Selettore del peso -->
              <select v-model.number="grade.weight" class="weight-select">
                <option value="1">100%</option>
                <option value="0.5">50%</option>
                <option value="0">Ignora</option>
              </select>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const username = ref('')
const password = ref('')
const error = ref('')
const isLoggedIn = ref(false)
const rawGrades = ref([])
let authToken = ''
let studentIdent = ''

// --- LOGICA API ---
const login = async () => {
  if (!username.value || !password.value) {
    error.value = "Inserisci username e password."
    return
  }
  
  error.value = "Accesso in corso..."
  
  try {
    // Puntiamo al nostro server Flask locale
    const res = await fetch('http://localhost:5000/api/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ uid: username.value, pass: password.value })
    })

    const data = await res.json()

    if (!res.ok) {
      throw new Error(data.error || data.message || "Credenziali errate o errore server.")
    }
    
    authToken = data.token
    studentIdent = data.ident.replace('G', 'S')
    isLoggedIn.value = true
    error.value = ''
    
    await fetchGrades()
    
  } catch (err) {
    error.value = err.message
  }
}

const fetchGrades = async () => {
  // Puntiamo sempre a Flask
  const res = await fetch(`http://localhost:5000/api/grades/${studentIdent}`, {
    headers: {
      'Z-Auth-Token': authToken
    }
  })
  
  const data = await res.json()
  
  rawGrades.value = data.grades
    .map((g, index) => ({
      id: index,
      display: g.displayValue,
      value: parseGrade(g.displayValue),
      subject: g.subjectDesc,
      date: g.evtDate,
      weight: 1.0
    }))
    .filter(g => g.value !== null)
}

// --- PARSER DEI VOTI ---
const parseGrade = (gradeStr) => {
  if (typeof gradeStr !== 'string') return null
  let g = gradeStr.toLowerCase().replace(',', '.')
  
  try {
    if (g.endsWith('+')) return parseFloat(g.slice(0, -1)) + 0.25
    if (g.endsWith('-')) return parseFloat(g.slice(0, -1)) - 0.25
    if (g.includes('½') || g.includes('mezzo')) return parseFloat(g.replace('½', '').replace('mezzo', '')) + 0.5
    if (g.includes('/')) {
      const parts = g.split('/')
      return (parseFloat(parts[0]) + parseFloat(parts[1])) / 2
    }
    const val = parseFloat(g)
    return isNaN(val) ? null : val
  } catch {
    return null
  }
}

// --- CALCOLO COMPUTED ---
const subjectsData = computed(() => {
  const subjects = {}
  rawGrades.value.forEach(grade => {
    if (!subjects[grade.subject]) {
      subjects[grade.subject] = { grades: [], sum: 0, weights: 0, average: 0 }
    }
    subjects[grade.subject].grades.push(grade)
    subjects[grade.subject].sum += grade.value * grade.weight
    subjects[grade.subject].weights += grade.weight
  })

  for (const key in subjects) {
    if (subjects[key].weights > 0) {
      subjects[key].average = subjects[key].sum / subjects[key].weights
    }
  }
  return subjects
})

const generalAverage = computed(() => {
  let totalSum = 0
  let totalWeights = 0
  for (const key in subjectsData.value) {
    const subj = subjectsData.value[key]
    if (subj.weights > 0) {
      totalSum += subj.average
      totalWeights += 1 
    }
  }
  return totalWeights === 0 ? 0 : totalSum / totalWeights
})

const getColor = (media) => {
  if (media < 5.5) return '#ef4444' // Rosso
  if (media < 6.0) return '#f59e0b' // Arancione
  return '#10b981' // Verde
}
</script>

<style scoped>
/* STILI DI BASE */
* {
  box-sizing: border-box;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

.container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
  color: #333;
}

.main-title {
  text-align: center;
  color: #1f2937;
  margin-bottom: 30px;
}

/* LOGIN BOX */
.login-box {
  max-width: 400px;
  margin: 50px auto;
  padding: 30px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.login-box h2 {
  margin-top: 0;
  text-align: center;
}

.input-field {
  padding: 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 16px;
}

.btn-primary {
  padding: 12px;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-primary:hover {
  background-color: #2563eb;
}

.error-msg {
  color: #ef4444;
  text-align: center;
  margin: 0;
  font-size: 14px;
}

/* DASHBOARD E SCHEDE MATERIE */
.general-average-card {
  text-align: center;
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
}

.general-average-card h2 {
  margin: 0;
  font-size: 28px;
}

.subjects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.subject-card {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.subject-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 2px solid #f3f4f6;
  padding-bottom: 10px;
  margin-bottom: 15px;
}

.subject-header h3 {
  margin: 0;
  font-size: 18px;
}

.grades-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.grade-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f3f4f6;
}

.grade-item:last-child {
  border-bottom: none;
}

.grade-info {
  display: flex;
  flex-direction: column;
}

.grade-value {
  font-weight: bold;
  font-size: 18px;
}

.grade-date {
  font-size: 12px;
  color: #6b7280;
}

.weight-select {
  padding: 6px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  background: #f9fafb;
}
</style>
