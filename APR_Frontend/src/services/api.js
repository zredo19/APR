import axios from 'axios';

// Creamos una instancia de Axios con la URL base de tu Backend
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor de Request: Agregar token JWT automáticamente
api.interceptors.request.use(
  (config) => {
    // Obtener token desde localStorage
    const token = localStorage.getItem('token');

    // Si existe el token, agregarlo al header Authorization
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor de Response: Manejar errores de autenticación
api.interceptors.response.use(
  (response) => {
    // Si la respuesta es exitosa, simplemente retornarla
    return response;
  },
  (error) => {
    // Si recibimos un error 401 (No autorizado)
    if (error.response && error.response.status === 401) {
      // Limpiar el token inválido
      localStorage.removeItem('token');
      localStorage.removeItem('user');

      // Redirigir al login (solo si no estamos ya en login)
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

export default api;