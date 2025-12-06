import { useState } from 'react';
import api from '../services/api';
import { Search, AlertTriangle, FileText, User } from 'lucide-react';

const Cliente = () => {
  const [rut, setRut] = useState('');
  const [usuario, setUsuario] = useState(null); // Datos del usuario (ID, nombre)
  const [cuentas, setCuentas] = useState([]);
  const [loading, setLoading] = useState(false);
  const [mensajeReporte, setMensajeReporte] = useState('');

  // 1. Buscar Usuario y Deudas
  const buscarCliente = async (e) => {
    e.preventDefault();
    setLoading(true);
    setUsuario(null);
    try {
      // Paso A: Obtener datos personales (ID, Nombre)
      const respUser = await api.get(`/usuarios/buscar/${rut}`);
      setUsuario(respUser.data);

      // Paso B: Obtener deudas
      const respCuentas = await api.get(`/usuarios/${rut}/cuenta`);
      setCuentas(respCuentas.data);
    } catch (error) {
      alert("RUT no encontrado o error en el sistema");
    } finally {
      setLoading(false);
    }
  };

  // 2. Enviar Reporte de Corte/Reclamo
  const enviarReporte = async () => {
    if (!usuario || !mensajeReporte) return;
    try {
      await api.post('/reportes/', {
        tipo: 'reclamo', // O 'corte', podrías hacerlo dinámico
        descripcion: mensajeReporte,
        usuario_id: usuario.id
      });
      alert("Reporte enviado correctamente. Te contactaremos pronto.");
      setMensajeReporte('');
    } catch (error) {
      alert("Error enviando reporte");
    }
  };

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <h2 className="text-3xl font-bold text-blue-800 mb-6 flex items-center gap-2">
        <User /> Portal de Socios
      </h2>

      {/* Buscador */}
      <div className="bg-white p-6 rounded-xl shadow-md mb-8">
        <form onSubmit={buscarCliente} className="flex gap-4 items-end">
          <div className="flex-1">
            <label className="block text-gray-700 font-bold mb-2">Ingresa tu RUT</label>
            <input 
              type="text" 
              placeholder="Ej: 12345678-9"
              className="w-full border p-3 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
              value={rut}
              onChange={(e) => setRut(e.target.value)}
            />
          </div>
          <button 
            type="submit" 
            className="bg-blue-600 text-white px-6 py-3 rounded-lg font-bold hover:bg-blue-700 transition flex items-center gap-2"
            disabled={loading}
          >
            <Search size={20} /> {loading ? 'Buscando...' : 'Consultar'}
          </button>
        </form>
      </div>

      {usuario && (
        <div className="grid md:grid-cols-2 gap-8">
          {/* Columna Izquierda: Datos y Cuentas */}
          <div className="space-y-6">
            <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
              <h3 className="font-bold text-blue-900 text-lg">{usuario.nombre_completo}</h3>
              <p className="text-gray-600">{usuario.direccion}</p>
              <span className="inline-block mt-2 bg-blue-200 text-blue-800 px-2 py-1 rounded text-xs font-bold uppercase">
                {usuario.sector.nombre}
              </span>
            </div>

            <div className="bg-white rounded-xl shadow overflow-hidden">
              <div className="bg-gray-100 p-4 border-b font-bold flex items-center gap-2">
                <FileText size={18} /> Estado de Cuenta
              </div>
              {cuentas.length === 0 ? (
                <p className="p-4 text-gray-500">No registras deudas pendientes.</p>
              ) : (
                <table className="w-full text-left">
                  <thead className="bg-gray-50 text-gray-600 text-sm">
                    <tr>
                      <th className="p-3">Periodo</th>
                      <th className="p-3">Vence</th>
                      <th className="p-3">Monto</th>
                      <th className="p-3">Estado</th>
                    </tr>
                  </thead>
                  <tbody>
                    {cuentas.map((c) => (
                      <tr key={c.id} className="border-t">
                        <td className="p-3">{c.periodo}</td>
                        <td className="p-3">{new Date(c.fecha_vencimiento).toLocaleDateString()}</td>
                        <td className="p-3 font-mono font-bold">${c.monto.toLocaleString()}</td>
                        <td className="p-3">
                          <span className={`px-2 py-1 rounded-full text-xs font-bold ${c.esta_pagada ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                            {c.esta_pagada ? 'Pagado' : 'Impago'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>

          {/* Columna Derecha: Reportar Problema */}
          <div className="bg-white p-6 rounded-xl shadow-md h-fit border-l-4 border-orange-500">
            <h3 className="font-bold text-xl mb-4 flex items-center gap-2 text-orange-700">
              <AlertTriangle /> ¿Tienes algún problema?
            </h3>
            <p className="text-gray-600 mb-4 text-sm">
              Reporta cortes de agua, fugas o problemas de facturación directamente a la central.
            </p>
            <textarea
              className="w-full border p-3 rounded-lg mb-4 h-32 resize-none focus:ring-2 focus:ring-orange-200 outline-none"
              placeholder="Describe tu problema aquí..."
              value={mensajeReporte}
              onChange={(e) => setMensajeReporte(e.target.value)}
            ></textarea>
            <button 
              onClick={enviarReporte}
              className="w-full bg-orange-600 text-white py-2 rounded-lg font-bold hover:bg-orange-700 transition"
            >
              Enviar Reporte
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Cliente;