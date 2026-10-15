import React from 'react';


export default function ToolTip({text}) {
   return (
    <span className="tooltip-wrapper">
      <span className="tooltip-icon">?</span>
      <span className="tooltip-content">
        {text}
      </span>
    </span>
  );
}
