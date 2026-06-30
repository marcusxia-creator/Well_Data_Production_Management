function selectedLabel(count) {
  if (!count) return "all";
  return count === 1 ? "1 selected" : count + " selected";
}

export default function MultiSelectDropdown({
  title,
  options,
  selected,
  onToggle,
  onClear,
  emptyText = "No options",
}) {
  return (
    <details className="multi-select-dropdown">
      <summary>
        <span>{title}</span>
        <strong>{selectedLabel(selected.length)}</strong>
      </summary>
      <div className="multi-select-menu">
        <div className="filter-title-row">
          <span>{title}</span>
          {selected.length > 0 && (
            <button type="button" className="link-button" onClick={onClear}>
              Clear
            </button>
          )}
        </div>
        <div className="choice-list">
          {options.map((option) => (
            <label key={option.value} className="choice-item">
              <input
                type="checkbox"
                checked={selected.includes(option.value)}
                onChange={() => onToggle(option.value)}
              />
              <span>{option.label}</span>
            </label>
          ))}
          {options.length === 0 && <p className="empty small">{emptyText}</p>}
        </div>
      </div>
    </details>
  );
}

export { selectedLabel };
