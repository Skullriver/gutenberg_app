import React, { useState } from 'react';

const ImageLoader = ({ src, alt }) => {
  const [loading, setLoading] = useState(true);

  return (
    <div>
      {loading && <div className="image-loader">Loading...</div>}
      <img
        src={src}
        alt={alt}
        style={{ display: loading ? 'none' : 'block' }}
        onLoad={() => setLoading(false)}
      />
    </div>
  );
};

export default ImageLoader;
