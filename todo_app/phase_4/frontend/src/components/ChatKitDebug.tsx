"use client";

/**
 * ChatKit Debug Component
 * Tests if ChatKit web component is properly defined
 */

import { useEffect, useState } from "react";

export function ChatKitDebug() {
  const [webComponentDefined, setWebComponentDefined] = useState(false);
  const [chatKitPackageExists, setChatKitPackageExists] = useState(false);

  useEffect(() => {
    // Check if openai-chatkit custom element is defined
    const isDefined = customElements.get('openai-chatkit') !== undefined;
    setWebComponentDefined(isDefined);

    // Try to import @openai/chatkit-react
    import('@openai/chatkit-react')
      .then(() => setChatKitPackageExists(true))
      .catch(() => setChatKitPackageExists(false));

    console.log('ChatKit Debug:', {
      customElementDefined: isDefined,
      customElements: customElements,
      window: typeof window !== 'undefined'
    });
  }, []);

  return (
    <div className="p-4 bg-gray-100 rounded border">
      <h2 className="text-lg font-bold mb-2">ChatKit Debug Info</h2>
      <div className="space-y-1 text-sm">
        <p>✅ Browser environment: {typeof window !== 'undefined' ? 'Yes' : 'No'}</p>
        <p>
          {webComponentDefined ? '✅' : '❌'}
          {' '}openai-chatkit web component defined: {webComponentDefined ? 'Yes' : 'No'}
        </p>
        <p>
          {chatKitPackageExists ? '✅' : '❌'}
          {' '}@openai/chatkit-react package: {chatKitPackageExists ? 'Loaded' : 'Failed'}
        </p>
      </div>
    </div>
  );
}
