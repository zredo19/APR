import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Home from './pages/Home';
import Cliente from './pages/Cliente';
import Personal from './pages/Personal';
import LoginPage from './pages/LoginPage';
import ProtectedRoute from './components/ProtectedRoute';
import ChatBot from './components/ChatBot';
import { LogOut, Lock } from 'lucide-react';

// Componente de navegación separado para poder usar useAuth
function Navigation() {
  const { isAuthenticated, logout, user } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <nav className="bg-blue-900 text-white shadow-lg">
      <div className="max-w-6xl mx-auto px-4">
        <div className="flex justify-between h-16 items-center">
          <Link to="/" className="font-bold text-xl">💧 APR Graneros</Link>
          <div className="flex items-center space-x-4">
            <Link to="/" className="hover:bg-blue-800 px-3 py-2 rounded transition">Inicio</Link>
            <Link to="/cliente" className="hover:bg-blue-800 px-3 py-2 rounded transition">Soy Cliente</Link>

            {isAuthenticated() ? (
              <>
                <Link to="/personal" className="hover:bg-blue-800 px-3 py-2 rounded transition">Personal</Link>
                <button
                  onClick={handleLogout}
                  className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded transition flex items-center gap-2 font-medium"
                >
                  <LogOut size={18} />
                  Cerrar Sesión
                </button>
              </>
            ) : (
              <Link
                to="/login"
                className="bg-blue-950 hover:bg-blue-900 px-4 py-2 rounded transition flex items-center gap-2 font-medium border border-blue-900 shadow-sm"
              >
                <Lock size={18} />
                Acceso Personal
              </Link>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}

function AppContent() {
  return (
    <div className="min-h-screen bg-slate-50 relative">
      <Navigation />

      {/* Contenido de las Páginas */}
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/cliente" element={<Cliente />} />
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/personal"
          element={
            <ProtectedRoute>
              <Personal />
            </ProtectedRoute>
          }
        />
      </Routes>
      <ChatBot />
    </div>
  );
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </Router>
  );
}

export default App;