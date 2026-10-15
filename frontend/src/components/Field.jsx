import ToolTip from "./ToolTip.jsx";

export default function Field({ label, toolText, children }) {
  return (
    <div className="field">
      <label className="field-label">
        {label}
        <ToolTip text={toolText} />
      </label>

      {children}
    </div>
  );
};
