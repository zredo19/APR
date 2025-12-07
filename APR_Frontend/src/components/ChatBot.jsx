import { useState, useRef, useEffect } from 'react';
import api from '../services/api';
import {
  MessageCircle, X, Send,
  Mic, MicOff, Volume2, VolumeX,
  ThumbsUp, ThumbsDown
} from 'lucide-react';

const ChatBot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { text: "¡Hola! Soy el asistente virtual. ¿En qué puedo ayudarte?", sender: 'bot' }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  // Estados para Voz
  const [isListening, setIsListening] = useState(false);
  const [audioEnabled, setAudioEnabled] = useState(false); // Por defecto apagado

  const messagesEndRef = useRef(null);

  // Scroll automático al fondo
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isOpen]);

  // Lectura de voz (Text-to-Speech)
  useEffect(() => {
    if (!audioEnabled) return;

    const lastMsg = messages[messages.length - 1];
    if (lastMsg && lastMsg.sender === 'bot') {
      const utterance = new SpeechSynthesisUtterance(lastMsg.text);
      utterance.lang = 'es-ES'; // Español
      window.speechSynthesis.speak(utterance);
    }
  }, [messages, audioEnabled]);

  // Manejo del Micrófono (Speech-to-Text)
  const toggleMic = () => {
    if (isListening) {
      setIsListening(false);
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Tu navegador no soporta reconocimiento de voz.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = 'es-CL'; // Español Chile
    recognition.interimResults = false;

    recognition.onstart = () => setIsListening(true);

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setInput(transcript);
    };

    recognition.onend = () => setIsListening(false);

    recognition.start();
  };

  // Enviar Mensaje
  const handleSend = async (e) => {
    if (e) e.preventDefault();
    if (!input.trim()) return;

    const userMsg = { text: input, sender: 'user' };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      // Detección simple de usuario (simulada por ahora)
      let userId = null;
      if (input.toLowerCase().includes("soy juan")) userId = 1;

      const response = await api.post('/chat/interactuar', {
        mensaje: userMsg.text,


      });

      // Guardamos la respuesta Y el ID para poder votar después
      const botMsg = {
        text: response.data.respuesta,
        sender: 'bot',
        id: response.data.id, // ID de la base de datos
        voted: false // Para saber si ya votó
      };
      setMessages(prev => [...prev, botMsg]);

    } catch (error) {
      setMessages(prev => [...prev, { text: "Error de conexión con el servidor.", sender: 'bot' }]);
    } finally {
      setLoading(false);
    }
  };

  // Función para Votar (Feedback)
  const handleVote = async (msgIndex, isUseful) => {
    const msg = messages[msgIndex];
    if (!msg.id) return;

    try {
      // Llamada al backend para guardar el feedback
      await api.put(`/chat/${msg.id}/feedback`, { es_util: isUseful });

      // Actualizamos el estado local para ocultar botones
      setMessages(prev => prev.map((m, idx) => {
        if (idx === msgIndex) {
          return { ...m, voted: true };
        }
        return m;
      }));

      alert("¡Gracias por tu opinión!");

    } catch (error) {
      console.error("Error enviando feedback", error);
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end">
      {/* Ventana de Chat */}
      {isOpen && (
        <div className="bg-white w-80 h-[500px] rounded-2xl shadow-2xl border border-gray-200 flex flex-col mb-4 overflow-hidden animate-fade-in-up">
          {/* Header */}
          <div className="bg-blue-600 p-4 text-white flex justify-between items-center shadow-md">
            <div className="flex items-center gap-2">
              <div className="bg-white/20 p-1.5 rounded-full">
                <MessageCircle size={20} />
              </div>
              <span className="font-bold">Asistente APR</span>
            </div>
            <div className="flex gap-2">
              {/* Botón de Audio (Mute/Unmute) */}
              <button
                onClick={() => setAudioEnabled(!audioEnabled)}
                className="hover:bg-blue-700 rounded p-1 transition"
                title={audioEnabled ? "Desactivar voz" : "Activar voz"}
              >
                {audioEnabled ? <Volume2 size={18} /> : <VolumeX size={18} />}
              </button>
              <button onClick={() => setIsOpen(false)} className="hover:bg-blue-700 rounded p-1 transition">
                <X size={18} />
              </button>
            </div>
          </div>

          {/* Mensajes */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50">
            {messages.map((msg, idx) => (
              <div key={idx} className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}>

                {/* Burbuja del mensaje */}
                <div className={`max-w-[85%] p-3 rounded-2xl text-sm shadow-sm ${msg.sender === 'user'
                  ? 'bg-blue-600 text-white rounded-br-none'
                  : 'bg-white border border-gray-200 text-gray-800 rounded-bl-none'
                  }`}>
                  {msg.text}
                </div>

                {/* Botones de Feedback (Solo si es bot, tiene ID y no ha votado) */}
                {msg.sender === 'bot' && msg.id && !msg.voted && (
                  <div className="flex gap-2 mt-1 ml-1">
                    <button
                      onClick={() => handleVote(idx, true)}
                      className="text-gray-400 hover:text-green-500 transition"
                      title="Útil"
                    >
                      <ThumbsUp size={14} />
                    </button>
                    <button
                      onClick={() => handleVote(idx, false)}
                      className="text-gray-400 hover:text-red-500 transition"
                      title="No útil"
                    >
                      <ThumbsDown size={14} />
                    </button>
                  </div>
                )}
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-gray-200 text-gray-500 text-xs px-3 py-2 rounded-full animate-pulse">
                  Escribiendo...
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <form onSubmit={handleSend} className="p-3 bg-white border-t flex gap-2 items-center">

            {/* Botón de Micrófono */}
            <button
              type="button"
              onClick={toggleMic}
              className={`p-2 rounded-full transition ${isListening ? 'bg-red-500 text-white animate-pulse' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              title="Dictar mensaje"
            >
              {isListening ? <MicOff size={18} /> : <Mic size={18} />}
            </button>

            <input
              type="text"
              className="flex-1 border border-gray-300 rounded-full px-4 py-2 text-sm focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition"
              placeholder={isListening ? "Escuchando..." : "Escribe tu consulta..."}
              value={input}
              onChange={(e) => setInput(e.target.value)}
            />

            <button
              type="submit"
              className="bg-blue-600 text-white p-2 rounded-full hover:bg-blue-700 transition shadow-md disabled:bg-blue-300"
              disabled={loading || !input.trim()}
            >
              <Send size={18} />
            </button>
          </form>
        </div>
      )}

      {/* Botón Flotante */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white p-4 rounded-full shadow-xl transition-transform hover:scale-105 flex items-center gap-2 animate-bounce-slow"
        >
          <MessageCircle size={28} />
          <span className="font-bold hidden md:block">¿Ayuda?</span>
        </button>
      )}
    </div>
  );
};

export default ChatBot;