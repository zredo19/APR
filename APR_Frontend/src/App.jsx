import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Home from './pages/Home';
import Cliente from './pages/Cliente';
import Personal from './pages/Personal';
import ChatBot from './components/ChatBot';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-slate-50 relative">
        {/* Barra de Navegación */}
        <nav className="bg-blue-900 text-white shadow-lg">
          <div className="max-w-6xl mx-auto px-4">
            <div className="flex justify-between h-16 items-center">
              <Link to="/" className="font-bold text-xl">💧 APR Graneros</Link>
              <div className="flex space-x-4">
                <Link to="/" className="hover:bg-blue-800 px-3 py-2 rounded transition">Inicio</Link>
                <Link to="/cliente" className="hover:bg-blue-800 px-3 py-2 rounded transition">Soy Cliente</Link>
                <Link to="/personal" className="hover:bg-blue-800 px-3 py-2 rounded transition">Personal</Link>
              </div>
            </div>
          </div>
        </nav>

        {/* Contenido de las Páginas */}
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/cliente" element={<Cliente />} />
          <Route path="/personal" element={<Personal />} />
        </Routes>
        <ChatBot />
      </div>
    </Router>
  );
}

export default App;