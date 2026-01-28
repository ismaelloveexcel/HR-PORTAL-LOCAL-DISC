import { useState } from "react";
import { Template } from "../../types/template";
import { templateService } from "../../services/templateService";

interface Props {
  template: Template | null;
  onClose: () => void;
}

export const TemplateEditor: React.FC<Props> = ({ template, onClose }) => {
  const [form, setForm] = useState<Partial<Template>>(
    template || { name: "", type: "document", content: "", revision_note: "" }
  );
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      if (template) {
        await templateService.update(template.id, form);
      } else {
        await templateService.create(form);
      }
      onClose();
    } catch (e) {
      setError("Failed to save template");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
      <form className="bg-white p-6 rounded shadow-lg w-full max-w-lg" onSubmit={handleSubmit}>
        <h3 className="text-xl font-bold mb-4">{template ? "Edit Template" : "New Template"}</h3>
        <div className="mb-2">
          <label className="block font-medium">Name</label>
          <input name="name" value={form.name || ""} onChange={handleChange} className="input input-bordered w-full" required />
        </div>
        <div className="mb-2">
          <label className="block font-medium">Type</label>
          <select name="type" value={form.type || "document"} onChange={handleChange} className="input input-bordered w-full">
            <option value="document">Document</option>
            <option value="letter">Letter</option>
            <option value="checklist">Checklist</option>
            <option value="timeline">Timeline</option>
            <option value="pass">Pass</option>
          </select>
        </div>
        <div className="mb-2">
          <label className="block font-medium">Content</label>
          <textarea name="content" value={form.content || ""} onChange={handleChange} className="input input-bordered w-full h-32" required />
        </div>
        <div className="mb-2">
          <label className="block font-medium">Revision Note</label>
          <input name="revision_note" value={form.revision_note || ""} onChange={handleChange} className="input input-bordered w-full" />
        </div>
        {error && <div className="text-red-600 mb-2">{error}</div>}
        <div className="flex justify-end space-x-2 mt-4">
          <button type="button" className="btn btn-secondary" onClick={onClose} disabled={saving}>Cancel</button>
          <button type="submit" className="btn btn-primary" disabled={saving}>{saving ? "Saving..." : "Save"}</button>
        </div>
      </form>
    </div>
  );
};
