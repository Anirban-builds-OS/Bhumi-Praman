// import type { FieldLocation } from "../types";

// interface Props {
//   imageUrl: string;
//   imageWidth: number | null;
//   imageHeight: number | null;
//   highlights: { field: string; location: FieldLocation; active: boolean }[];
// }

// export default function DocumentCanvas({ imageUrl, imageWidth, imageHeight, highlights }: Props) {
//   return (
//     <div className="doc-canvas rounded-lg border border-border overflow-hidden relative">
//       <div className="relative w-full" style={{ aspectRatio: imageWidth && imageHeight ? `${imageWidth} / ${imageHeight}` : "3 / 4" }}>
//         <img src={imageUrl} alt="Source document" className="absolute inset-0 w-full h-full object-contain" draggable={false} />
//         {imageWidth && imageHeight && highlights.map(({ field, location, active }) => (
//           <div
//             key={field}
//             className={`ocr-zone ${active ? "ocr-zone-active" : ""}`}
//             style={{
//               left: `${(location.left / imageWidth) * 100}%`,
//               top: `${(location.top / imageHeight) * 100}%`,
//               width: `${(location.width / imageWidth) * 100}%`,
//               height: `${(location.height / imageHeight) * 100}%`,
//               opacity: active ? 1 : 0.55,
//             }}
//           />
//         ))}
//       </div>
//     </div>
//   );
// }

import { useEffect, useState } from "react";
import type { FieldLocation } from "../types";

interface Props {
  imageUrl: string;
  imageWidth: number | null;
  imageHeight: number | null;
  highlights: {
    field: string;
    location: FieldLocation;
    active: boolean;
  }[];
}

export default function DocumentCanvas({
  imageUrl,
  imageWidth,
  imageHeight,
  highlights,
}: Props) {
  const [imageSrc, setImageSrc] = useState<string | null>(null);
  const [imageError, setImageError] = useState(false);

  useEffect(() => {
    let objectUrl: string | null = null;

    const loadImage = async () => {
      try {
        setImageError(false);
        setImageSrc(null);

        const token = localStorage.getItem("bp_token");

        const response = await fetch(imageUrl, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error(
            `Failed to load document image: ${response.status}`
          );
        }

        const blob = await response.blob();

        objectUrl = URL.createObjectURL(blob);
        setImageSrc(objectUrl);
      } catch (error) {
        console.error("Failed to load source document:", error);
        setImageError(true);
      }
    };

    if (imageUrl) {
      loadImage();
    }

    return () => {
      if (objectUrl) {
        URL.revokeObjectURL(objectUrl);
      }
    };
  }, [imageUrl]);

  return (
    <div className="doc-canvas rounded-lg border border-border overflow-hidden relative">
      <div
        className="relative w-full"
        style={{
          aspectRatio:
            imageWidth && imageHeight
              ? `${imageWidth} / ${imageHeight}`
              : "3 / 4",
        }}
      >
        {imageSrc && !imageError && (
          <img
            src={imageSrc}
            alt="Source document"
            className="absolute inset-0 w-full h-full object-contain"
            draggable={false}
          />
        )}

        {!imageSrc && !imageError && (
          <div className="absolute inset-0 flex items-center justify-center text-muted-foreground">
            Loading document...
          </div>
        )}

        {imageError && (
          <div className="absolute inset-0 flex items-center justify-center text-red-500">
            Failed to load document
          </div>
        )}

        {imageWidth &&
          imageHeight &&
          highlights.map(({ field, location, active }) => (
            <div
              key={field}
              className={`ocr-zone ${
                active ? "ocr-zone-active" : ""
              }`}
              style={{
                left: `${(location.left / imageWidth) * 100}%`,
                top: `${(location.top / imageHeight) * 100}%`,
                width: `${(location.width / imageWidth) * 100}%`,
                height: `${(location.height / imageHeight) * 100}%`,
                opacity: active ? 1 : 0.55,
              }}
            />
          ))}
      </div>
    </div>
  );
}