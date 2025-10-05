/**
 * FAQ Page
 * Frequently Asked Questions for authenticated users
 */

import React, { useState } from 'react';
import { ChevronDown, ChevronRight, HelpCircle } from 'lucide-react';

// FAQ data for authenticated users
const FAQ_ITEMS = [
  {
    question: 'How do I submit a new report?',
    answer: 'Navigate to the \'Reports\' section from your main dashboard and click the \'Submit New Report\' button. You will be guided through the process of uploading and validating your report file.'
  },
  {
    question: 'What is the purpose of the chat system?',
    answer: 'The chat system provides a secure and direct line of communication with UKNF staff. You can use it to ask questions about your reports, clarify requirements, or resolve any issues you encounter.'
  },
  {
    question: 'How can I edit my organization\'s (Subject) details?',
    answer: 'If you have \'Subject Admin\' permissions, you can navigate to the \'Manage Subjects\' section from the main menu. There you will find the option to edit your organization\'s information.'
  },
  {
    question: 'Where can I see the history of changes to my organization\'s details?',
    answer: 'The complete audit trail for your organization is available on the \'Manage Subjects\' page. This history tracks all changes, including who made them and when.'
  }
];

export const FAQPage: React.FC = () => {
  const [openFAQ, setOpenFAQ] = useState<number | null>(null);

  const toggleFAQ = (index: number) => {
    setOpenFAQ(openFAQ === index ? null : index);
  };

  return (
    <div className="p-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-600 rounded-full mb-4">
            <HelpCircle className="text-white" size={32} />
          </div>
          <h1 className="text-3xl font-bold text-gray-900">Frequently Asked Questions</h1>
          <p className="text-gray-600 mt-2">Find answers to common questions about the UKNF Report Desk</p>
        </div>

        {/* FAQ Accordion */}
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-lg shadow-lg overflow-hidden">
            <div className="space-y-0">
              {FAQ_ITEMS.map((item, index) => (
                <div key={index} className="border-b border-gray-200 last:border-b-0">
                  <button
                    onClick={() => toggleFAQ(index)}
                    className="w-full px-6 py-4 text-left hover:bg-gray-50 transition-colors flex items-center justify-between focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-inset"
                  >
                    <span className="text-lg font-medium text-gray-900 pr-4">{item.question}</span>
                    {openFAQ === index ? (
                      <ChevronDown className="text-gray-500 flex-shrink-0" size={20} />
                    ) : (
                      <ChevronRight className="text-gray-500 flex-shrink-0" size={20} />
                    )}
                  </button>
                  {openFAQ === index && (
                    <div className="px-6 pb-4 bg-gray-50">
                      <p className="text-gray-700 leading-relaxed">{item.answer}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Additional Help Section */}
        <div className="max-w-4xl mx-auto mt-8">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-blue-900 mb-2">Need More Help?</h3>
            <p className="text-blue-800 mb-4">
              If you can't find the answer to your question here, you can:
            </p>
            <ul className="text-blue-800 space-y-2">
              <li className="flex items-start">
                <span className="text-blue-600 mr-2">•</span>
                Use the chat system to contact UKNF staff directly
              </li>
              <li className="flex items-start">
                <span className="text-blue-600 mr-2">•</span>
                Contact your organization's primary administrator
              </li>
              <li className="flex items-start">
                <span className="text-blue-600 mr-2">•</span>
                Review the user documentation and guides
              </li>
            </ul>
          </div>
        </div>
      </div>
  );
};
