import React, { useState, useEffect } from 'react';
import { CheckCircle, ChevronRight } from 'lucide-react';
import { API_BASE } from '../config';
import { trackEvent } from '../analytics';

interface OnboardingFlowProps {
  token: string | null;
}

const ROLES = ['DevOps Engineer', 'SRE', 'Platform Engineer', 'Backend Developer', 'Full-Stack Developer', 'Other'];

const OnboardingFlow: React.FC<OnboardingFlowProps> = ({ token }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [step, setStep] = useState(1);
  const [role, setRole] = useState('');
  const [tools, setTools] = useState<{ id: number; name: string }[]>([]);
  const [selectedTools, setSelectedTools] = useState<number[]>([]);

  useEffect(() => {
    const completed = localStorage.getItem('onboarding_complete');
    if (completed || !token) return;
    setIsOpen(true);
    fetchTools();
  }, [token]);

  const fetchTools = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/tools`);
      if (res.ok) {
        const data = await res.json();
        setTools(data.slice(0, 30).map((t: { id: number; name: string }) => ({ id: t.id, name: t.name })));
      }
    } catch { /* ignore */ }
  };

  const toggleTool = (id: number) => {
    setSelectedTools((prev) =>
      prev.includes(id) ? prev.filter((t) => t !== id) : [...prev, id]
    );
  };

  const saveStack = async () => {
    if (!token) return;
    for (const toolId of selectedTools) {
      try {
        await fetch(`${API_BASE}/api/users/me/stack/${toolId}`, {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}` },
        });
      } catch { /* ignore */ }
    }
  };

  const handleComplete = async () => {
    await saveStack();
    localStorage.setItem('onboarding_complete', 'true');
    localStorage.setItem('user_role', role);
    trackEvent('onboarding_completed', { role, tools_selected: selectedTools.length });
    setIsOpen(false);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-lg w-full p-6">
        {/* Progress bar */}
        <div className="flex gap-2 mb-6">
          {[1, 2, 3].map((s) => (
            <div
              key={s}
              className={`h-1.5 flex-1 rounded-full ${s <= step ? 'bg-blue-600' : 'bg-gray-200'}`}
            />
          ))}
        </div>

        {step === 1 && (
          <div>
            <h2 className="text-xl font-bold text-gray-900 mb-1">Welcome to CloudEngineered!</h2>
            <p className="text-gray-500 mb-5">What best describes your role?</p>
            <div className="space-y-2">
              {ROLES.map((r) => (
                <button
                  key={r}
                  onClick={() => setRole(r)}
                  className={`w-full text-left px-4 py-3 rounded-lg border transition-colors ${
                    role === r
                      ? 'border-blue-500 bg-blue-50 text-blue-700'
                      : 'border-gray-200 hover:border-gray-300 text-gray-700'
                  }`}
                >
                  {r}
                </button>
              ))}
            </div>
            <button
              onClick={() => role && setStep(2)}
              disabled={!role}
              className="mt-5 w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center gap-2"
            >
              Continue <ChevronRight size={18} />
            </button>
          </div>
        )}

        {step === 2 && (
          <div>
            <h2 className="text-xl font-bold text-gray-900 mb-1">Your current stack</h2>
            <p className="text-gray-500 mb-5">Select tools you currently use (we'll personalize your experience)</p>
            <div className="flex flex-wrap gap-2 max-h-64 overflow-y-auto">
              {tools.map((t) => (
                <button
                  key={t.id}
                  onClick={() => toggleTool(t.id)}
                  className={`px-3 py-1.5 rounded-full text-sm border transition-colors ${
                    selectedTools.includes(t.id)
                      ? 'border-blue-500 bg-blue-50 text-blue-700'
                      : 'border-gray-200 hover:border-gray-300 text-gray-600'
                  }`}
                >
                  {t.name}
                </button>
              ))}
            </div>
            <button
              onClick={() => setStep(3)}
              className="mt-5 w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 flex items-center justify-center gap-2"
            >
              Continue <ChevronRight size={18} />
            </button>
          </div>
        )}

        {step === 3 && (
          <div className="text-center py-4">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <CheckCircle className="text-green-600" size={32} />
            </div>
            <h2 className="text-xl font-bold text-gray-900 mb-2">You're all set!</h2>
            <p className="text-gray-500 mb-6">
              We've personalized your experience as a {role}
              {selectedTools.length > 0 ? ` with ${selectedTools.length} tools in your stack` : ''}.
            </p>
            <button
              onClick={handleComplete}
              className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700"
            >
              Start Exploring
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default OnboardingFlow;
