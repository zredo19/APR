import { useEffect, useState } from 'react';
import api from '../services/api';
import { Map, AlertOctagon, CheckCircle, Search, User, FileText, UploadCloud } from 'lucide-react';

const Personal = () => {
  // Estado para Sectores
  const [sectores, setSectores] = useState([]);

  // Estado para Buscador de Clientes
  const [rutBusqueda, setRutBusqueda] = useState('');
  const [clienteEncontrado, setClienteEncontrado] = useState(null);
  const [loadingCliente, setLoadingCliente] = useState(false);

  // Estado para Carga Masiva
  const [archivoExcel, setArchivoExcel] = useState(null);
  const [loadingUpload, setLoadingUpload] = useState(false);

  // Cargar sectores al inicio
  const cargarSectores = async () => {
    try {
      const resp = await api.get('/sectores/');
      setSectores(resp.data);
    } catch (error) {
      console.error("Error cargando sectores");
    }
  };

  useEffect(() => {
    cargarSectores();
  }, []);

  // Función para activar/desactivar cortes
  const toggleCorte = async (sector) => {
    try {
      const nuevoEstado = !sector.tiene_corte;
      await api.put(`/sectores/${sector.id}`, {
        tiene_corte: nuevoEstado,
        mensaje_alerta: nuevoEstado ? "Corte de emergencia en curso" : "Servicio normal"
      });
      cargarSectores();
    } catch (error) {
      alert("Error actualizando el sector");
    }
  };

  // Función para buscar cliente (Admin)
  const buscarCliente = async (e) => {
    e.preventDefault();
    setLoadingCliente(true);
    setClienteEncontrado(null);
    try {
      // 1. Buscamos datos básicos
      const respUser = await api.get(`/usuarios/buscar/${rutBusqueda}`);
      const usuario = respUser.data;

      // 2. Buscamos sus cuentas
      const respCuentas = await api.get(`/usuarios/${rutBusqueda}/cuenta`);

      setClienteEncontrado({ ...usuario, cuentas: respCuentas.data });
    } catch (error) {
      alert("Cliente no encontrado en la base de datos.");
    } finally {
      setLoadingCliente(false);
    }
  };

  // Función para manejar la carga masiva de Excel
  const handleFileUpload = async () => {
    if (!archivoExcel) {
      alert('Por favor selecciona un archivo Excel primero');
      return;
    }

    setLoadingUpload(true);
    try {
      const formData = new FormData();
      formData.append('archivo', archivoExcel);

      const response = await api.post('/admin/importar-excel', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      // Mostrar resumen de la importación
      const { mensaje, resumen } = response.data;
      alert(
        `✅ ${mensaje}\n\n` +
        `📊 Resumen:\n` +
        `• Filas procesadas: ${resumen.filas_procesadas}\n` +
        `• Sectores creados: ${resumen.sectores_creados}\n` +
        `• Usuarios creados: ${resumen.usuarios_creados}\n` +
        `• Usuarios actualizados: ${resumen.usuarios_actualizados}\n` +
        `• Cuentas creadas: ${resumen.cuentas_creadas}\n` +
        `• Cuentas actualizadas: ${resumen.cuentas_actualizadas}`
      );

      // Limpiar el input y refrescar sectores
      setArchivoExcel(null);
      document.getElementById('file-input').value = '';
      cargarSectores();
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Error al procesar el archivo';
      alert(`❌ Error: ${errorMsg}`);
    } finally {
      setLoadingUpload(false);
    }
  };

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-12">

      {/* SECCIÓN 0: OPERACIONES MASIVAS */}
      <section>
        <h2 className="text-3xl font-bold text-indigo-900 mb-6 flex items-center gap-2">
          <UploadCloud /> Operaciones Masivas
        </h2>
        <div className="bg-gradient-to-br from-indigo-50 to-blue-50 p-8 rounded-2xl border-2 border-dashed border-indigo-300 shadow-lg hover:shadow-xl transition-shadow">
          <div className="max-w-2xl">
            <h3 className="text-2xl font-bold text-indigo-900 mb-3 flex items-center gap-2">
              📊 Cargar Planilla Mensual
            </h3>
            <p className="text-gray-700 mb-6 leading-relaxed">
              Sube el Excel con los consumos del mes para actualizar usuarios y deudas automáticamente.
              El archivo debe contener las columnas: <span className="font-mono text-sm bg-white px-2 py-1 rounded">rut</span>,
              <span className="font-mono text-sm bg-white px-2 py-1 rounded mx-1">nombre</span>,
              <span className="font-mono text-sm bg-white px-2 py-1 rounded">direccion</span>,
              <span className="font-mono text-sm bg-white px-2 py-1 rounded mx-1">sector</span>,
              <span className="font-mono text-sm bg-white px-2 py-1 rounded">monto_deuda</span>,
              <span className="font-mono text-sm bg-white px-2 py-1 rounded mx-1">periodo_deuda</span>.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
              <div className="flex-1">
                <label
                  htmlFor="file-input"
                  className="block text-sm font-bold text-gray-700 mb-2"
                >
                  Seleccionar archivo Excel:
                </label>
                <input
                  id="file-input"
                  type="file"
                  accept=".xlsx,.xls"
                  onChange={(e) => setArchivoExcel(e.target.files[0])}
                  className="block w-full text-sm text-gray-700 file:mr-4 file:py-3 file:px-6 file:rounded-lg file:border-0 file:text-sm file:font-bold file:bg-indigo-100 file:text-indigo-700 hover:file:bg-indigo-200 file:cursor-pointer cursor-pointer bg-white border-2 border-gray-300 rounded-lg focus:outline-none focus:border-indigo-500 transition"
                />
                {archivoExcel && (
                  <p className="mt-2 text-sm text-green-600 font-medium">
                    ✓ Archivo seleccionado: {archivoExcel.name}
                  </p>
                )}
              </div>

              <button
                onClick={handleFileUpload}
                disabled={!archivoExcel || loadingUpload}
                className="bg-indigo-600 text-white px-8 py-3 rounded-lg font-bold hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center gap-2 shadow-md hover:shadow-lg transition-all mt-6 sm:mt-0"
              >
                <UploadCloud size={20} />
                {loadingUpload ? 'Procesando...' : 'Subir Excel'}
              </button>
            </div>
          </div>
        </div>
      </section>

      <hr className="border-gray-300" />

      {/* SECCIÓN 1: CONTROL DE SECTORES */}
      <section>
        <h2 className="text-3xl font-bold text-indigo-900 mb-6 flex items-center gap-2">
          <Map /> Gestión de Sectores y Cortes
        </h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {sectores.map((sector) => (
            <div
              key={sector.id}
              className={`p-6 rounded-xl border-2 shadow-sm transition-all ${sector.tiene_corte ? 'bg-red-50 border-red-400' : 'bg-white border-gray-100'
                }`}
            >
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-xl font-bold text-gray-800">{sector.nombre}</h3>
                {sector.tiene_corte ? (
                  <AlertOctagon className="text-red-500 animate-pulse" />
                ) : (
                  <CheckCircle className="text-green-500" />
                )}
              </div>
              <button
                onClick={() => toggleCorte(sector)}
                className={`w-full py-2 rounded-lg font-bold text-sm transition ${sector.tiene_corte
                    ? 'bg-green-600 hover:bg-green-700 text-white'
                    : 'bg-red-100 hover:bg-red-200 text-red-700'
                  }`}
              >
                {sector.tiene_corte ? 'Restaurar Servicio' : 'REPORTAR CORTE'}
              </button>
            </div>
          ))}
        </div>
      </section>

      <hr className="border-gray-300" />

      {/* SECCIÓN 2: BUSCADOR DE CLIENTES (ADMIN) */}
      <section>
        <h2 className="text-3xl font-bold text-slate-800 mb-6 flex items-center gap-2">
          <User /> Atención al Cliente
        </h2>
        <div className="bg-white p-6 rounded-xl shadow-lg border border-gray-200">
          <form onSubmit={buscarCliente} className="flex gap-4 mb-6">
            <input
              type="text"
              placeholder="RUT del cliente (Ej: 12345678-9)"
              className="flex-1 border p-3 rounded-lg outline-none focus:ring-2 focus:ring-indigo-500"
              value={rutBusqueda}
              onChange={(e) => setRutBusqueda(e.target.value)}
            />
            <button
              type="submit"
              className="bg-indigo-600 text-white px-6 py-3 rounded-lg font-bold hover:bg-indigo-700 flex items-center gap-2"
              disabled={loadingCliente}
            >
              <Search size={20} /> Buscar
            </button>
          </form>

          {clienteEncontrado && (
            <div className="bg-slate-50 p-6 rounded-lg border border-slate-200 animate-fade-in">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-xl font-bold text-slate-900">{clienteEncontrado.nombre_completo}</h3>
                  <p className="text-slate-600">{clienteEncontrado.direccion}</p>
                  <p className="text-sm text-indigo-600 font-bold mt-1">Sector: {clienteEncontrado.sector.nombre}</p>
                </div>
                <div className="bg-white p-2 rounded border text-center min-w-[100px]">
                  <p className="text-xs text-gray-500 uppercase">Total Deuda</p>
                  <p className="text-xl font-bold text-red-600">
                    ${clienteEncontrado.cuentas.filter(c => !c.esta_pagada).reduce((acc, curr) => acc + curr.monto, 0).toLocaleString()}
                  </p>
                </div>
              </div>

              <h4 className="font-bold text-gray-700 mb-3 flex items-center gap-2 border-b pb-2">
                <FileText size={16} /> Historial de Cuentas
              </h4>
              <ul className="space-y-2">
                {clienteEncontrado.cuentas.map(c => (
                  <li key={c.id} className="flex justify-between text-sm p-2 bg-white rounded border">
                    <span>Periodo: <b>{c.periodo}</b></span>
                    <span className={c.esta_pagada ? "text-green-600 font-bold" : "text-red-500 font-bold"}>
                      {c.esta_pagada ? "PAGADO" : "PENDIENTE"}
                    </span>
                    <span>${c.monto.toLocaleString()}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </section>

    </div>
  );
};

export default Personal;