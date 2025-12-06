import { useState, useRef, useEffect } from 'react';
import api from '../services/api';
import { MessageCircle, X, Send } from 'lucide-react';

const ChatBot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { text: "¡Hola! Soy el asistente virtual. ¿En qué puedo ayudarte?", sender: 'bot' }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isOpen]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg = { text: input, sender: 'user' };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      let userId = null;
      if (input.toLowerCase().includes("soy juan")) userId = 1;

      const response = await api.post('/chat/interactuar', {
        mensaje_usuario: userMsg.text,
        respuesta_bot: "",
        usuario_id: userId
      });

      const botMsg = { text: response.data.respuesta, sender: 'bot' };
      setMessages(prev => [...prev, botMsg]);

    } catch (error) {
      setMessages(prev => [...prev, { text: "Error de conexión con el servidor.", sender: 'bot' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end">
      {/* Ventana de Chat */}
      {isOpen && (
        <div className="bg-white w-80 h-96 rounded-2xl shadow-2xl border border-gray-200 flex flex-col mb-4 overflow-hidden">
          {/* Header */}
          <div className="bg-blue-600 p-4 text-white flex justify-between items-center">
            <div className="flex items-center gap-2">
              <div className="bg-white/20 p-1.5 rounded-full">
                <MessageCircle size={20} />
              </div>
              <span className="font-bold">Asistente APR</span>
            </div>
            <button onClick={() => setIsOpen(false)} className="hover:bg-blue-700 rounded p-1">
              <X size={18} />
            </button>
          </div>

          {/* Mensajes */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-50">
            {messages.map((msg, idx) => (
              <div key={idx} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] p-3 rounded-lg text-sm ${
                  msg.sender === 'user' 
                    ? 'bg-blue-600 text-white rounded-br-none' 
                    : 'bg-white border text-gray-800 rounded-bl-none shadow-sm'
                }`}>
                  {msg.text}
                </div>
              </div>
            ))}
            {loading && <div className="text-xs text-gray-400 p-2">Escribiendo...</div>}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <form onSubmit={handleSend} className="p-3 bg-white border-t flex gap-2">
            <input
              type="text"
              className="flex-1 border rounded-full px-4 py-2 text-sm focus:outline-none focus:border-blue-500"
              placeholder="Escribe tu consulta..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
            />
            <button type="submit" className="bg-blue-600 text-white p-2 rounded-full hover:bg-blue-700 transition">
              <Send size={18} />
            </button>
          </form>
        </div>
      )}

      {/* Botón Flotante */}
      {!isOpen && (
        <button 
          onClick={() => setIsOpen(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white p-4 rounded-full shadow-lg transition-transform hover:scale-110 flex items-center gap-2"
        >
          <MessageCircle size={28} />
          <span className="font-bold hidden md:block">¿Ayuda?</span>
        </button>
      )}
    </div>
  );
};

export default ChatBot;