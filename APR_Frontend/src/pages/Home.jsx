import { useEffect, useState } from 'react';
import api from '../services/api';
import { Droplets, Phone } from 'lucide-react';

const Home = () => {
  const [info, setInfo] = useState(null);

  useEffect(() => {
    // Consumimos el endpoint que creamos en el backend
    api.get('/info/estado-servicio')
      .then(response => setInfo(response.data))
      .catch(error => console.error("Error cargando info", error));
  }, []);

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-blue-900 flex justify-center items-center gap-3">
          <Droplets className="w-10 h-10 text-blue-500" />
          Cooperativa de Agua APR
        </h1>
        <p className="text-gray-600 mt-2">Portal de Servicios Digitales y Atención IA</p>
      </div>

      {info ? (
        <div className="grid md:grid-cols-2 gap-6">
          <div className="bg-white p-6 rounded-xl shadow-md border-l-4 border-blue-500">
            <h3 className="font-bold text-lg mb-2">Horario de Atención</h3>
            <p className="text-gray-700">{info.horario}</p>
          </div>
          <div className="bg-white p-6 rounded-xl shadow-md border-l-4 border-red-500">
            <h3 className="font-bold text-lg mb-2 flex items-center gap-2">
              <Phone className="w-5 h-5" /> Emergencias
            </h3>
            <p className="text-gray-700 font-mono text-xl">{info.fono_emergencia}</p>
          </div>
        </div>
      ) : (
        <p className="text-center">Cargando estado del servicio...</p>
      )}
    </div>
  );
};

export default Home;