import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
    User, Mail, Calendar, Edit3, Save, X, Shield,
    Github, Chrome, Settings, Activity, LogOut,
    Camera, CheckCircle, AlertCircle, Loader
} from 'lucide-react';
import { API_BASE } from '../config';

interface UserProfile {
    id: number;
    username: string;
    email: string;
    avatar_url?: string;
    bio?: string;
    github_connected: boolean;
    google_connected: boolean;
    oauth_provider?: string;
    created_at: string;
}

const ProfilePage: React.FC = () => {
    const [profile, setProfile] = useState<UserProfile | null>(null);
    const [loading, setLoading] = useState(true);
    const [editing, setEditing] = useState(false);
    const [saving, setSaving] = useState(false);
    const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);

    const [editForm, setEditForm] = useState({
        username: '',
        bio: ''
    });

    useEffect(() => {
        fetchProfile();
    }, []);

    const fetchProfile = async () => {
        const token = localStorage.getItem('token');
        if (!token) {
            setLoading(false);
            return;
        }

        try {
            const response = await fetch(`${API_BASE}/api/auth/me`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (response.ok) {
                const data = await response.json();
                setProfile(data);
                setEditForm({
                    username: data.username || '',
                    bio: data.bio || ''
                });
            }
        } catch (error) {
            console.error('Failed to fetch profile:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleSaveProfile = async () => {
        const token = localStorage.getItem('token');
        if (!token) return;

        setSaving(true);
        setMessage(null);

        try {
            const response = await fetch(`${API_BASE}/api/users/profile`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(editForm)
            });

            if (response.ok) {
                setMessage({ type: 'success', text: 'Profile updated successfully!' });
                setEditing(false);
                fetchProfile();
            } else {
                setMessage({ type: 'error', text: 'Failed to update profile' });
            }
        } catch (error) {
            setMessage({ type: 'error', text: 'An error occurred' });
        } finally {
            setSaving(false);
        }
    };

    const handleConnectOAuth = async (provider: string) => {
        try {
            const response = await fetch(`${API_BASE}/api/auth/oauth/${provider}/authorize`);
            const data = await response.json();

            if (data.authorization_url) {
                window.location.href = data.authorization_url;
            }
        } catch (error) {
            setMessage({ type: 'error', text: `Failed to connect ${provider}` });
        }
    };

    const formatDate = (dateString: string) => {
        if (!dateString) return 'Unknown';
        try {
            const date = new Date(dateString);
            return date.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
        } catch {
            return 'Unknown';
        }
    };

    const getInitials = (name: string) => {
        return name?.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2) || 'U';
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 flex items-center justify-center">
                <div className="flex items-center space-x-3">
                    <Loader className="animate-spin text-blue-600" size={32} />
                    <span className="text-gray-600 text-lg">Loading profile...</span>
                </div>
            </div>
        );
    }

    if (!profile) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 flex items-center justify-center">
                <div className="text-center bg-white rounded-2xl shadow-xl p-12 max-w-md">
                    <div className="w-20 h-20 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-full flex items-center justify-center mx-auto mb-6">
                        <User className="text-blue-600" size={40} />
                    </div>
                    <h2 className="text-2xl font-bold text-gray-900 mb-3">Sign in to view your profile</h2>
                    <p className="text-gray-500 mb-6">Access your account settings and manage your profile</p>
                    <Link
                        to="/login"
                        className="inline-flex items-center px-8 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-semibold rounded-xl hover:from-blue-700 hover:to-indigo-700 transition-all shadow-lg hover:shadow-xl"
                    >
                        Sign In
                    </Link>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
            {/* Header Background */}
            <div className="h-48 bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 relative overflow-hidden">
                <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZGVmcz48cGF0dGVybiBpZD0iZ3JpZCIgd2lkdGg9IjQwIiBoZWlnaHQ9IjQwIiBwYXR0ZXJuVW5pdHM9InVzZXJTcGFjZU9uVXNlIj48cGF0aCBkPSJNIDQwIDAgTCAwIDAgMCA0MCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSJyZ2JhKDI1NSwyNTUsMjU1LDAuMSkiIHN0cm9rZS13aWR0aD0iMSIvPjwvcGF0dGVybj48L2RlZnM+PHJlY3Qgd2lkdGg9IjEwMCUiIGhlaWdodD0iMTAwJSIgZmlsbD0idXJsKCNncmlkKSIvPjwvc3ZnPg==')] opacity-30"></div>
            </div>

            <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 -mt-24 pb-12">
                {/* Profile Card */}
                <div className="bg-white rounded-2xl shadow-2xl overflow-hidden">
                    {/* Profile Header */}
                    <div className="p-8 pb-6">
                        <div className="flex flex-col sm:flex-row items-start sm:items-end gap-6">
                            {/* Avatar */}
                            <div className="relative group">
                                {profile.avatar_url ? (
                                    <img
                                        src={profile.avatar_url}
                                        alt={profile.username}
                                        className="w-32 h-32 rounded-2xl object-cover border-4 border-white shadow-xl"
                                    />
                                ) : (
                                    <div className="w-32 h-32 rounded-2xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white text-4xl font-bold border-4 border-white shadow-xl">
                                        {getInitials(profile.username)}
                                    </div>
                                )}
                                <button className="absolute bottom-2 right-2 p-2 bg-white rounded-full shadow-lg opacity-0 group-hover:opacity-100 transition-opacity">
                                    <Camera size={16} className="text-gray-600" />
                                </button>
                            </div>

                            {/* Profile Info */}
                            <div className="flex-1">
                                <div className="flex items-start justify-between">
                                    <div>
                                        <h1 className="text-3xl font-bold text-gray-900">{profile.username}</h1>
                                        <p className="text-gray-500 flex items-center mt-1">
                                            <Mail size={16} className="mr-2" />
                                            {profile.email}
                                        </p>
                                        {profile.bio && (
                                            <p className="text-gray-600 mt-2 max-w-lg">{profile.bio}</p>
                                        )}
                                    </div>

                                    {!editing && (
                                        <button
                                            onClick={() => setEditing(true)}
                                            className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-xl text-gray-700 transition-colors"
                                        >
                                            <Edit3 size={18} />
                                            Edit Profile
                                        </button>
                                    )}
                                </div>

                                <div className="flex items-center gap-6 mt-4 text-sm text-gray-500">
                                    <div className="flex items-center gap-2">
                                        <Calendar size={16} />
                                        Joined {formatDate(profile.created_at)}
                                    </div>
                                    {profile.oauth_provider && (
                                        <div className="flex items-center gap-2 px-3 py-1 bg-green-50 text-green-700 rounded-full">
                                            <CheckCircle size={14} />
                                            Signed in with {profile.oauth_provider}
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Message */}
                    {message && (
                        <div className={`mx-8 mb-6 p-4 rounded-xl flex items-center gap-3 ${message.type === 'success'
                            ? 'bg-green-50 text-green-700 border border-green-200'
                            : 'bg-red-50 text-red-700 border border-red-200'
                            }`}>
                            {message.type === 'success' ? <CheckCircle size={20} /> : <AlertCircle size={20} />}
                            {message.text}
                        </div>
                    )}

                    {/* Edit Form */}
                    {editing && (
                        <div className="mx-8 mb-6 p-6 bg-gray-50 rounded-xl border border-gray-200">
                            <h3 className="text-lg font-semibold text-gray-900 mb-4">Edit Profile</h3>
                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">Username</label>
                                    <input
                                        type="text"
                                        value={editForm.username}
                                        onChange={(e) => setEditForm({ ...editForm, username: e.target.value })}
                                        className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">Bio</label>
                                    <textarea
                                        value={editForm.bio}
                                        onChange={(e) => setEditForm({ ...editForm, bio: e.target.value })}
                                        rows={3}
                                        placeholder="Tell us about yourself..."
                                        className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                                    />
                                </div>
                                <div className="flex gap-3">
                                    <button
                                        onClick={handleSaveProfile}
                                        disabled={saving}
                                        className="flex items-center gap-2 px-6 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-medium rounded-xl hover:from-blue-700 hover:to-indigo-700 disabled:opacity-50"
                                    >
                                        {saving ? <Loader className="animate-spin" size={18} /> : <Save size={18} />}
                                        Save Changes
                                    </button>
                                    <button
                                        onClick={() => {
                                            setEditing(false);
                                            setEditForm({ username: profile.username, bio: profile.bio || '' });
                                        }}
                                        className="flex items-center gap-2 px-6 py-2.5 bg-gray-200 text-gray-700 font-medium rounded-xl hover:bg-gray-300"
                                    >
                                        <X size={18} />
                                        Cancel
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Sections Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 p-8 pt-2">
                        {/* Connected Accounts */}
                        <div className="bg-gradient-to-br from-gray-50 to-slate-50 rounded-xl p-6 border border-gray-100">
                            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                                <Shield size={20} className="text-blue-600" />
                                Connected Accounts
                            </h3>
                            <div className="space-y-3">
                                <div className="flex items-center justify-between p-4 bg-white rounded-xl border border-gray-200">
                                    <div className="flex items-center gap-3">
                                        <div className="w-10 h-10 bg-gray-900 rounded-lg flex items-center justify-center">
                                            <Github className="text-white" size={20} />
                                        </div>
                                        <div>
                                            <p className="font-medium text-gray-900">GitHub</p>
                                            <p className="text-sm text-gray-500">
                                                {profile.github_connected ? 'Connected' : 'Not connected'}
                                            </p>
                                        </div>
                                    </div>
                                    {profile.github_connected ? (
                                        <span className="px-3 py-1 bg-green-100 text-green-700 text-sm font-medium rounded-full">
                                            Connected
                                        </span>
                                    ) : (
                                        <button
                                            onClick={() => handleConnectOAuth('github')}
                                            className="px-4 py-2 bg-gray-900 text-white text-sm font-medium rounded-lg hover:bg-gray-800"
                                        >
                                            Connect
                                        </button>
                                    )}
                                </div>

                                <div className="flex items-center justify-between p-4 bg-white rounded-xl border border-gray-200">
                                    <div className="flex items-center gap-3">
                                        <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-red-500 rounded-lg flex items-center justify-center">
                                            <Chrome className="text-white" size={20} />
                                        </div>
                                        <div>
                                            <p className="font-medium text-gray-900">Google</p>
                                            <p className="text-sm text-gray-500">
                                                {profile.google_connected ? 'Connected' : 'Not connected'}
                                            </p>
                                        </div>
                                    </div>
                                    {profile.google_connected ? (
                                        <span className="px-3 py-1 bg-green-100 text-green-700 text-sm font-medium rounded-full">
                                            Connected
                                        </span>
                                    ) : (
                                        <button
                                            onClick={() => handleConnectOAuth('google')}
                                            className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700"
                                        >
                                            Connect
                                        </button>
                                    )}
                                </div>
                            </div>
                        </div>

                        {/* Activity Stats */}
                        <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-100">
                            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                                <Activity size={20} className="text-indigo-600" />
                                Activity
                            </h3>
                            <div className="grid grid-cols-2 gap-4">
                                <div className="bg-white/80 backdrop-blur rounded-xl p-4 text-center">
                                    <p className="text-3xl font-bold text-blue-600">0</p>
                                    <p className="text-sm text-gray-600">Tools Reviewed</p>
                                </div>
                                <div className="bg-white/80 backdrop-blur rounded-xl p-4 text-center">
                                    <p className="text-3xl font-bold text-indigo-600">0</p>
                                    <p className="text-sm text-gray-600">Comparisons</p>
                                </div>
                                <div className="bg-white/80 backdrop-blur rounded-xl p-4 text-center">
                                    <p className="text-3xl font-bold text-purple-600">0</p>
                                    <p className="text-sm text-gray-600">Articles Read</p>
                                </div>
                                <div className="bg-white/80 backdrop-blur rounded-xl p-4 text-center">
                                    <p className="text-3xl font-bold text-green-600">0</p>
                                    <p className="text-sm text-gray-600">Comments</p>
                                </div>
                            </div>
                        </div>

                        {/* Account Settings */}
                        <div className="bg-gradient-to-br from-amber-50 to-orange-50 rounded-xl p-6 border border-amber-100">
                            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                                <Settings size={20} className="text-amber-600" />
                                Account Settings
                            </h3>
                            <div className="space-y-3">
                                <button className="w-full flex items-center justify-between p-4 bg-white rounded-xl border border-gray-200 hover:bg-gray-50 transition-colors">
                                    <span className="font-medium text-gray-700">Change Password</span>
                                    <span className="text-gray-400">→</span>
                                </button>
                                <button className="w-full flex items-center justify-between p-4 bg-white rounded-xl border border-gray-200 hover:bg-gray-50 transition-colors">
                                    <span className="font-medium text-gray-700">Email Preferences</span>
                                    <span className="text-gray-400">→</span>
                                </button>
                                <button className="w-full flex items-center justify-between p-4 bg-white rounded-xl border border-gray-200 hover:bg-gray-50 transition-colors">
                                    <span className="font-medium text-gray-700">Privacy Settings</span>
                                    <span className="text-gray-400">→</span>
                                </button>
                            </div>
                        </div>

                        {/* Danger Zone */}
                        <div className="bg-gradient-to-br from-red-50 to-rose-50 rounded-xl p-6 border border-red-100">
                            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                                <LogOut size={20} className="text-red-600" />
                                Session & Security
                            </h3>
                            <div className="space-y-3">
                                <button
                                    onClick={() => {
                                        localStorage.removeItem('token');
                                        localStorage.removeItem('user');
                                        window.location.href = '/';
                                    }}
                                    className="w-full flex items-center justify-center gap-2 p-4 bg-white rounded-xl border border-red-200 text-red-600 font-medium hover:bg-red-50 transition-colors"
                                >
                                    <LogOut size={18} />
                                    Sign Out
                                </button>
                                <button className="w-full flex items-center justify-center gap-2 p-4 bg-white rounded-xl border border-red-200 text-red-600 font-medium hover:bg-red-50 transition-colors">
                                    Sign Out All Devices
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ProfilePage;
