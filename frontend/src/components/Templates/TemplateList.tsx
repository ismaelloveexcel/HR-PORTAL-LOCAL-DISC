import { useEffect, useState } from "react";
import { templateService } from "../../services/templateService";
import { Template } from "../../types/template";
import { TemplateEditor } from "./TemplateEditor";

export const TemplateList: React.FC = () => {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [selected, setSelected] = useState<Template | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showEditor, setShowEditor] = useState(false);

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    setLoading(true);
    try {
      const data = await templateService.list();
      setTemplates(data);
    } catch (e) {
      setError("Failed to load templates");
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (template: Template) => {
    setSelected(template);
    setShowEditor(true);
  };

  const handleNew = () => {
    setSelected(null);
    setShowEditor(true);
  };

  const handleCloseEditor = () => {
    setShowEditor(false);
    loadTemplates();
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div className="text-red-600">{error}</div>;

  return (
    <div className="p-4">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold">Templates</h2>
        <button className="btn btn-primary" onClick={handleNew}>New Template</button>
      </div>
      <table className="min-w-full bg-white border">
        <thead>
          <tr>
            <th className="px-4 py-2">Name</th>
            <th className="px-4 py-2">Type</th>
            <th className="px-4 py-2">Version</th>
            <th className="px-4 py-2">Active</th>
            <th className="px-4 py-2">Actions</th>
          </tr>
        </thead>
        <tbody>
          {templates.map((t) => (
            <tr key={t.id}>
              <td className="px-4 py-2">{t.name}</td>
              <td className="px-4 py-2">{t.type}</td>
              <td className="px-4 py-2">{t.version}</td>
              <td className="px-4 py-2">{t.is_active ? "Yes" : "No"}</td>
              <td className="px-4 py-2">
                <button className="btn btn-sm btn-secondary mr-2" onClick={() => handleEdit(t)}>Edit</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {showEditor && (
        <TemplateEditor template={selected} onClose={handleCloseEditor} />
      )}
    </div>
  );
};
