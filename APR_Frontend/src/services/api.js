import axios from 'axios';

// Creamos una instancia de Axios con la URL base de tu Backend
const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;