/**
 * Manage Subjects Page
 * Displays a list of subjects that the current user has permission to manage
 */

import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { Building2, Settings, AlertCircle, Users } from 'lucide-react';
import { adminAPI } from '../services/api';
import type { Subject } from '../types';

const ManageSubjectsPage: React.FC = () => {
  const { data: subjects, isLoading, error } = useQuery({
    queryKey: ['manageableSubjects'],
    queryFn: () => adminAPI.getManageableSubjects(),
    retry: 1,
  });

  if (isLoading) {
    return (
      <div className="p-8">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <span className="ml-4 text-gray-600">Loading subjects...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <div className="flex items-center">
            <AlertCircle className="text-red-600 mr-3" size={24} />
            <div>
              <h3 className="text-lg font-medium text-red-800">Error Loading Subjects</h3>
              <p className="text-red-600 mt-1">
                Failed to fetch manageable subjects. Please try again later.
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <div className="flex items-center mb-4">
          <Building2 className="text-blue-600 mr-3" size={32} />
          <h1 className="text-3xl font-bold text-gray-900">Manage Subjects</h1>
        </div>
        <p className="text-gray-600">
          Select a subject to manage its details, users, and settings.
        </p>
      </div>

      {subjects && subjects.length > 0 ? (
        <div className="bg-white shadow-sm rounded-lg border border-gray-200 overflow-hidden">
          <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900">
              Manageable Subjects ({subjects.length})
            </h2>
          </div>
          
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Subject Details
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Contact Information
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {subjects.map((subject: Subject) => (
                  <tr key={subject.ID} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4">
                      <div>
                        <div className="flex items-center">
                          <Building2 className="text-gray-400 mr-2" size={16} />
                          <div>
                            <p className="text-sm font-medium text-gray-900">
                              {subject.NAME_STRUCTURE || 'Unnamed Subject'}
                            </p>
                            <p className="text-sm text-gray-500">
                              {subject.TYPE_STRUCTURE || 'No type specified'}
                            </p>
                          </div>
                        </div>
                        {(subject.NIP || subject.KRS || subject.LEI) && (
                          <div className="mt-2 text-xs text-gray-500">
                            {subject.NIP && <span>NIP: {subject.NIP}</span>}
                            {subject.KRS && <span className="ml-3">KRS: {subject.KRS}</span>}
                            {subject.LEI && <span className="ml-3">LEI: {subject.LEI}</span>}
                          </div>
                        )}
                      </div>
                    </td>
                    
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900">
                        {subject.EMAIL && (
                          <p className="mb-1">{subject.EMAIL}</p>
                        )}
                        {subject.PHONE && (
                          <p className="text-gray-500">{subject.PHONE}</p>
                        )}
                        {subject.TOWN && (
                          <p className="text-gray-500 text-xs mt-1">
                            {subject.TOWN}
                            {subject.POST_CODE && `, ${subject.POST_CODE}`}
                          </p>
                        )}
                      </div>
                    </td>
                    
                    <td className="px-6 py-4">
                      <div className="flex items-center">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          subject.VALIDATED 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-yellow-100 text-yellow-800'
                        }`}>
                          {subject.VALIDATED ? 'Validated' : 'Pending Validation'}
                        </span>
                        {subject.STATUS_S && (
                          <span className="ml-2 text-xs text-gray-500">
                            {subject.STATUS_S}
                          </span>
                        )}
                      </div>
                    </td>
                    
                    <td className="px-6 py-4 text-right">
                      <Link
                        to={`/subjects/${subject.ID}/manage`}
                        className="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
                      >
                        <Settings size={16} className="mr-2" />
                        Manage
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="bg-white shadow-sm rounded-lg border border-gray-200 p-12">
          <div className="text-center">
            <Users className="mx-auto text-gray-400 mb-4" size={48} />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No Manageable Subjects
            </h3>
            <p className="text-gray-600 mb-6">
              You do not have permission to manage any subjects. Contact your administrator 
              if you believe this is an error.
            </p>
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 max-w-md mx-auto">
              <p className="text-sm text-blue-800">
                <strong>Note:</strong> Only UKNF Administrators and Subject Administrators 
                can manage subjects.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ManageSubjectsPage;
