import React, { useState, useEffect } from 'react';
import { Apple, Bot, Rocket } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

// Poznámka: Pokud nemáš tyhle UI komponenty, nahradíme je obyčejnými divy
const Card = ({ children, className, onClick }: any) => (
  <div onClick={onClick} className={`bg-white rounded-xl shadow-sm border ${className}`}>{children}</div>
);
const CardContent = ({ children, className }: any) => (
  <div className={`p-6 ${className}`}>{children}</div>
);

export default function Dashboard() {
  const navigate = useNavigate();
  const [platform, setPlatform] = useState('android');
  const [metrics, setMetrics] = useState({
    total: 0, passed: 0, failed: 0, passRate: 0, avgDuration: 0, chartData: []
  });

  useEffect(() => {
    fetch(`https://float-thermal-facecloth.ngrok-free.dev/api/metrics?platform=${platform}`)
      .then(res => res.json())
      .then(data => setMetrics(data))
      .catch(err => console.error("API Error:", err));
  }, [platform]);

  return (
    <main className="p-8 bg-gray-50 min-h-screen">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Maestro Dashboard</h1>
        
        <div className="flex items-center gap-4">
          <div className="flex bg-gray-200 p-1 rounded-lg">
            <button 
              onClick={() => setPlatform('android')}
              className={`p-2 rounded-md ${platform === 'android' ? 'bg-white shadow-sm text-green-600' : 'text-gray-500'}`}
            >
              <Bot size={20} />
            </button>
            <button 
              onClick={() => setPlatform('ios')}
              className={`p-2 rounded-md ${platform === 'ios' ? 'bg-white shadow-sm text-blue-600' : 'text-gray-500'}`}
            >
              <Apple size={20} />
            </button>
          </div>
          <button className="flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors">
            <Rocket size={18} />
            Deploy
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card><CardContent><p className="text-sm text-gray-500">Total</p><p className="text-2xl font-bold">{metrics.total}</p></CardContent></Card>
        <Card className="border-l-4 border-green-500"><CardContent><p className="text-sm text-gray-500">Passed</p><p className="text-2xl font-bold text-green-600">{metrics.passed}</p></CardContent></Card>
        <Card className="border-l-4 border-red-500"><CardContent><p className="text-sm text-gray-500">Failed</p><p className="text-2xl font-bold text-red-600">{metrics.failed}</p></CardContent></Card>
        <Card><CardContent><p className="text-sm text-gray-500">Success Rate</p><p className="text-2xl font-bold">{metrics.passRate}%</p></CardContent></Card>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
         <Card onClick={() => navigate("/dashboard/vw")} className="cursor-pointer hover:border-indigo-500">
            <CardContent className="flex flex-col items-center py-10">
               <span className="text-xl font-bold">Volkswagen</span>
            </CardContent>
         </Card>
         <Card onClick={() => navigate("/dashboard/skoda")} className="cursor-pointer hover:border-indigo-500">
            <CardContent className="flex flex-col items-center py-10">
               <span className="text-xl font-bold">Skoda</span>
            </CardContent>
         </Card>
      </div>
    </main>
  );
}