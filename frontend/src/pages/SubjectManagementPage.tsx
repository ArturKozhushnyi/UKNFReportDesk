/**
 * Subject Management Page
 * Allows authorized users to edit subject details and view change history
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Save, History, AlertCircle, CheckCircle, ArrowLeft } from 'lucide-react';
import { adminAPI } from '../services/api';
import type { Subject } from '../types';

interface HistoryRecord {
  HISTORY_ID: number;
  OPERATION_TYPE: string;
  MODIFIED_AT: string;
  MODIFIED_BY: number | null;
  ID: number;
  NAME_STRUCTURE: string | null;
  [key: string]: any;
}

export const SubjectManagementPage: React.FC = () => {
  const { subjectId } = useParams<{ subjectId: string }>();
  const navigate = useNavigate();

  const [subject, setSubject] = useState<Subject | null>(null);
  const [history, setHistory] = useState<HistoryRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Form state
  const [formData, setFormData] = useState<Partial<Subject>>({});

  // Check if user can edit (they must be admin of this subject)
  const canEdit = true; // We'll rely on backend authorization

  useEffect(() => {
    if (subjectId) {
      loadSubject();
      loadHistory();
    }
  }, [subjectId]);

  const loadSubject = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await adminAPI.getSubject(Number(subjectId));
      setSubject(data);
      setFormData(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load subject');
    } finally {
      setLoading(false);
    }
  };

  const loadHistory = async () => {
    try {
      setLoadingHistory(true);
      const data = await adminAPI.getSubjectHistory(Number(subjectId));
      setHistory(data);
    } catch (err: any) {
      console.error('Failed to load history:', err);
    } finally {
      setLoadingHistory(false);
    }
  };

  const handleInputChange = (field: keyof Subject, value: any) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    setSuccess('');

    try {
      // Only send changed fields
      const changedFields: Partial<Subject> = {};
      Object.keys(formData).forEach((key) => {
        const k = key as keyof Subject;
        if (formData[k] !== subject?.[k]) {
          (changedFields as any)[k] = formData[k];
        }
      });

      if (Object.keys(changedFields).length === 0) {
        setSuccess('No changes to save');
        return;
      }

      const updated = await adminAPI.updateSubject(Number(subjectId), changedFields);
      setSubject(updated);
      setFormData(updated);
      setSuccess('Subject updated successfully!');
      
      // Reload history to show the new change
      loadHistory();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update subject');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!subject) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800">Subject not found</p>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => navigate(-1)}
          className="flex items-center text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeft size={20} className="mr-2" />
          Back
        </button>
        <h1 className="text-3xl font-bold text-gray-900">Subject Management</h1>
        <p className="text-gray-600 mt-2">Manage subject details and view change history</p>
      </div>

      {/* Alerts */}
      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4 flex items-start">
          <AlertCircle className="text-red-600 mr-2 flex-shrink-0" size={20} />
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      {success && (
        <div className="mb-6 bg-green-50 border border-green-200 rounded-lg p-4 flex items-start">
          <CheckCircle className="text-green-600 mr-2 flex-shrink-0" size={20} />
          <p className="text-sm text-green-800">{success}</p>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Edit Form */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Subject Details</h2>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Name
                  </label>
                  <input
                    type="text"
                    value={formData.NAME_STRUCTURE || ''}
                    onChange={(e) => handleInputChange('NAME_STRUCTURE', e.target.value)}
                    disabled={!canEdit}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Type
                  </label>
                  <input
                    type="text"
                    value={formData.TYPE_STRUCTURE || ''}
                    onChange={(e) => handleInputChange('TYPE_STRUCTURE', e.target.value)}
                    disabled={!canEdit}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    NIP
                  </label>
                  <input
                    type="text"
                    value={formData.NIP || ''}
                    onChange={(e) => handleInputChange('NIP', e.target.value)}
                    disabled={!canEdit}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    KRS
                  </label>
                  <input
                    type="text"
                    value={formData.KRS || ''}
                    onChange={(e) => handleInputChange('KRS', e.target.value)}
                    disabled={!canEdit}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Street
                  </label>
                  <input
                    type="text"
                    value={formData.STREET || ''}
                    onChange={(e) => handleInputChange('STREET', e.target.value)}
                    disabled={!canEdit}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Town
                  </label>
                  <input
                    type="text"
                    value={formData.TOWN || ''}
                    onChange={(e) => handleInputChange('TOWN', e.target.value)}
                    disabled={!canEdit}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Post Code
                  </label>
                  <input
                    type="text"
                    value={formData.POST_CODE || ''}
                    onChange={(e) => handleInputChange('POST_CODE', e.target.value)}
                    disabled={!canEdit}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Phone
                  </label>
                  <input
                    type="text"
                    value={formData.PHONE || ''}
                    onChange={(e) => handleInputChange('PHONE', e.target.value)}
                    disabled={!canEdit}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100"
                  />
                </div>

                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email
                  </label>
                  <input
                    type="email"
                    value={formData.EMAIL || ''}
                    onChange={(e) => handleInputChange('EMAIL', e.target.value)}
                    disabled={!canEdit}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Status
                  </label>
                  <input
                    type="text"
                    value={formData.STATUS_S || ''}
                    onChange={(e) => handleInputChange('STATUS_S', e.target.value)}
                    disabled={!canEdit}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100"
                  />
                </div>
              </div>

              {canEdit && (
                <div className="flex justify-end mt-6">
                  <button
                    type="submit"
                    disabled={saving}
                    className="flex items-center px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-blue-300 disabled:cursor-not-allowed"
                  >
                    {saving ? (
                      <>
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                        Saving...
                      </>
                    ) : (
                      <>
                        <Save size={20} className="mr-2" />
                        Save Changes
                      </>
                    )}
                  </button>
                </div>
              )}
            </form>
          </div>
        </div>

        {/* History Sidebar */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <History size={20} className="mr-2" />
              Change History
            </h2>

            {loadingHistory ? (
              <div className="flex justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              </div>
            ) : history.length === 0 ? (
              <p className="text-gray-500 text-sm">No changes recorded yet</p>
            ) : (
              <div className="space-y-4">
                {history.map((record) => (
                  <div
                    key={record.HISTORY_ID}
                    className="border-l-4 border-blue-500 pl-4 py-2"
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs font-semibold text-blue-600 uppercase">
                        {record.OPERATION_TYPE}
                      </span>
                      <span className="text-xs text-gray-500">
                        {new Date(record.MODIFIED_AT).toLocaleDateString()}
                      </span>
                    </div>
                    <p className="text-sm text-gray-700">
                      {record.NAME_STRUCTURE || 'Unknown Subject'}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      {new Date(record.MODIFIED_AT).toLocaleTimeString()}
                    </p>
                    {record.MODIFIED_BY && (
                      <p className="text-xs text-gray-500">
                        By User ID: {record.MODIFIED_BY}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

