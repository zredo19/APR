import { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [token, setToken] = useState(null);
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    // Cargar token desde localStorage al iniciar
    useEffect(() => {
        const storedToken = localStorage.getItem('token');
        const storedUser = localStorage.getItem('user');

        if (storedToken && storedUser) {
            setToken(storedToken);
            setUser(JSON.parse(storedUser));
        }

        setLoading(false);
    }, []);

    // Función para iniciar sesión
    const login = async (rut, password) => {
        try {
            // Crear FormData para OAuth2PasswordRequestForm
            const formData = new FormData();
            formData.append('username', rut);
            formData.append('password', password);

            const API_URL = import.meta.env.VITE_API_URL;

            const response = await axios.post(`${API_URL}/token`, formData, {
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
            });

            const { access_token } = response.data;

            // Guardar token
            setToken(access_token);
            localStorage.setItem('token', access_token);

            // Guardar información básica del usuario
            const userData = { rut };
            setUser(userData);
            localStorage.setItem('user', JSON.stringify(userData));

            return { success: true };
        } catch (error) {
            console.error('Error en login:', error);
            return {
                success: false,
                error: error.response?.data?.detail || 'Error al iniciar sesión'
            };
        }
    };

    // Función para cerrar sesión
    const logout = () => {
        setToken(null);
        setUser(null);
        localStorage.removeItem('token');
        localStorage.removeItem('user');
    };

    // Verificar si está autenticado
    const isAuthenticated = () => {
        return !!token;
    };

    const value = {
        token,
        user,
        login,
        logout,
        isAuthenticated,
        loading,
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Hook personalizado para usar el contexto
export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth debe ser usado dentro de un AuthProvider');
    }
    return context;
};
