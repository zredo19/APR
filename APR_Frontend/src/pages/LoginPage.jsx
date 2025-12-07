import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LogIn, User, Lock, AlertCircle } from 'lucide-react';

const LoginPage = () => {
    const [rut, setRut] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        // Validaciones básicas
        if (!rut || !password) {
            setError('Por favor ingresa tu RUT y contraseña');
            setLoading(false);
            return;
        }

        // Intentar login
        const result = await login(rut, password);

        if (result.success) {
            // Redirigir al panel de administración
            navigate('/personal');
        } else {
            setError(result.error);
        }

        setLoading(false);
    };

    return (
        <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-4">
            <div className="w-full max-w-md">
                {/* Card de Login */}
                <div className="bg-white rounded-2xl shadow-2xl p-8 border border-gray-100">
                    {/* Header */}
                    <div className="text-center mb-8">
                        <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full mb-4">
                            <LogIn className="text-white" size={32} />
                        </div>
                        <h1 className="text-3xl font-bold text-gray-800 mb-2">Iniciar Sesión</h1>
                        <p className="text-gray-600">Panel de Administración APR Graneros</p>
                    </div>

                    {/* Mensaje de Error */}
                    {error && (
                        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
                            <AlertCircle className="text-red-500 flex-shrink-0 mt-0.5" size={20} />
                            <p className="text-red-700 text-sm">{error}</p>
                        </div>
                    )}

                    {/* Formulario */}
                    <form onSubmit={handleSubmit} className="space-y-6">
                        {/* Campo RUT */}
                        <div>
                            <label htmlFor="rut" className="block text-sm font-bold text-gray-700 mb-2">
                                RUT
                            </label>
                            <div className="relative">
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                    <User className="text-gray-400" size={20} />
                                </div>
                                <input
                                    id="rut"
                                    type="text"
                                    placeholder="12345678-9"
                                    value={rut}
                                    onChange={(e) => setRut(e.target.value)}
                                    className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition"
                                    disabled={loading}
                                />
                            </div>
                        </div>

                        {/* Campo Contraseña */}
                        <div>
                            <label htmlFor="password" className="block text-sm font-bold text-gray-700 mb-2">
                                Contraseña
                            </label>
                            <div className="relative">
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                    <Lock className="text-gray-400" size={20} />
                                </div>
                                <input
                                    id="password"
                                    type="password"
                                    placeholder="••••••••"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition"
                                    disabled={loading}
                                />
                            </div>
                        </div>

                        {/* Botón Submit */}
                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-3 rounded-lg font-bold hover:from-blue-700 hover:to-indigo-700 disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl flex items-center justify-center gap-2"
                        >
                            {loading ? (
                                <>
                                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                                    Iniciando sesión...
                                </>
                            ) : (
                                <>
                                    <LogIn size={20} />
                                    Iniciar Sesión
                                </>
                            )}
                        </button>
                    </form>

                    {/* Footer */}
                    <div className="mt-6 pt-6 border-t border-gray-200 text-center">
                        <p className="text-sm text-gray-600">
                            Solo personal autorizado puede acceder
                        </p>
                    </div>
                </div>

                {/* Información adicional */}
                <div className="mt-6 text-center">
                    <p className="text-sm text-gray-600">
                        ¿Problemas para acceder?{' '}
                        <a href="tel:+56999999999" className="text-indigo-600 hover:text-indigo-700 font-medium">
                            Contacta al administrador
                        </a>
                    </p>
                </div>
            </div>
        </div>
    );
};

export default LoginPage;
