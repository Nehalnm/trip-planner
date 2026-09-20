import { useState, useEffect, useRef } from "react";
import { uploadPhoto, getPhotos } from "../api";

interface Photo {
  id: string;
  filename: string;
  uploaded_by: string;
}

function PhotoGallery({ tripId }: { tripId: string }) {
  const [photos, setPhotos] = useState<Photo[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    loadPhotos();
  }, [tripId]);

  async function loadPhotos() {
    const data = await getPhotos(tripId);
    setPhotos(data);
  }

  async function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    await uploadPhoto(tripId, file);
    loadPhotos();

    if (fileInputRef.current) fileInputRef.current.value = "";
  }

  return (
    <div>
      <input type="file" accept="image/*" ref={fileInputRef} onChange={handleFileChange} />

      <div style={{ display: "flex", flexWrap: "wrap", gap: "8px", marginTop: "8px" }}>
        {photos.map((photo) => (
          <img
            key={photo.id}
            src={`http://localhost:8000/photos/${photo.filename}`}
            alt="Trip"
            style={{ width: "150px", height: "150px", objectFit: "cover" }}
          />
        ))}
      </div>
    </div>
  );
}

export default PhotoGallery;