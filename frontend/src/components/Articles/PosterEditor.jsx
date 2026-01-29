
import React, { useEffect, useRef, useState } from 'react';
import { fabric } from 'fabric';
import api from '../../services/api';
import { FaSpinner, FaSave, FaTimes, FaUndo, FaRedo } from 'react-icons/fa';

const PosterEditor = ({ articleId, onClose, onSaveSuccess }) => {
    const canvasRef = useRef(null);
    const [fabricCanvas, setFabricCanvas] = useState(null);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [config, setConfig] = useState(null);
    const [templateName, setTemplateName] = useState("Standard Poster (Top Text)");
    const [activeObject, setActiveObject] = useState(null);

    // Initial Fetch
    useEffect(() => {
        fetchConfig();
    }, [articleId]);

    const fetchConfig = async () => {
        try {
            setLoading(true);
            const res = await api.get(`cms/articles/${articleId}/poster_editor_config/`, {
                params: { template: templateName }
            });
            setConfig(res.data);
            setLoading(false);
        } catch (error) {
            console.error("Failed to load poster config", error);
            setLoading(false);
        }
    };

    // Initialize Canvas once config is loaded
    useEffect(() => {
        if (!config || fabricCanvas) return;

        // Canvas Size (Scaled down for display if needed, but we usually want 1:1 for export quality)
        // Let's assume we render at a reasonable scale and export at full resolution.
        // For simplicity, let's try to match the template dims or a fixed height.
        // The Standard Poster is usually 1080x1350. That's too big for laptop screen.
        // We will scale everything down visually using CSS or fabric's zoom, but keep canvas big.

        // Better approach: Set canvas width/height to actual pixel format (1080x1350) 
        // and use CSS 'transform: scale()' to fit on screen.

        const initCanvas = new fabric.Canvas(canvasRef.current, {
            width: 1080,
            height: 1350,
            backgroundColor: '#000',
            preserveObjectStacking: true // Selected object stays in its Z-index
        });

        setFabricCanvas(initCanvas);

        initCanvas.on('selection:created', (e) => setActiveObject(e.selected[0]));
        initCanvas.on('selection:updated', (e) => setActiveObject(e.selected[0]));
        initCanvas.on('selection:cleared', () => setActiveObject(null));

        // Cleanup
        return () => {
            initCanvas.dispose();
        };
    }, [config]);

    // Load Content into Canvas
    useEffect(() => {
        if (!fabricCanvas || !config) return;

        fabricCanvas.clear();

        // 1. Background Image (Locked)
        if (config.template.background_url) {
            fabric.Image.fromURL(config.template.background_url, (img) => {
                img.set({
                    originX: 'left',
                    originY: 'top',
                    selectable: false,
                    evented: false,
                    scaleX: 1,
                    scaleY: 1
                });
                // Ensure it fits? Usually template is exactly 1080x1350
                fabricCanvas.setBackgroundImage(img, fabricCanvas.renderAll.bind(fabricCanvas));
            }, { crossOrigin: 'anonymous' });
        }

        // 2. Cutout Image (Movable)
        if (config.assets.cutout_url) {
            fabric.Image.fromURL(config.assets.cutout_url, (img) => {
                const imgConfig = config.template.image_config?.image_fields?.find(f => f.name === 'featured_image') || {};

                // Apply config logic (Simplified version of backend logic)
                const targetW = imgConfig.width || 1080;
                const targetH = imgConfig.height || 600;
                const x = imgConfig.x || 0;
                const y = imgConfig.y || 600;

                // Use 'contain' logic roughly
                const scale = Math.min(targetW / img.width, targetH / img.height);
                // Or just make it big enough

                img.set({
                    left: x + (targetW - (img.width * scale)) / 2, // Center horizontally in target area
                    top: y + (targetH - (img.height * scale)), // Align bottom of target area
                    scaleX: scale,
                    scaleY: scale,
                    originX: 'left',
                    originY: 'top',
                    borderColor: '#00ffff',
                    cornerColor: '#00ffff',
                    cornerSize: 20,
                    transparentCorners: false
                });
                fabricCanvas.add(img);
            }, { crossOrigin: 'anonymous' });
        }

        // 3. Text Layers
        const textConfig = config.template.text_config?.text_fields || [];

        textConfig.forEach(field => {
            let textVal = "";
            if (field.name === 'headline') textVal = config.content.headline;
            if (field.name === 'summary') textVal = config.content.summary;

            if (!textVal) textVal = field.name;

            const textObj = new fabric.Textbox(textVal, {
                left: field.x,
                top: field.y,
                width: field.max_width || 900,
                fontSize: field.font_size || 50,
                fill: field.color || '#ffffff',
                textAlign: field.align || 'center',
                fontFamily: 'Arial', // Start with standard, load custom font if possible
                fontWeight: 'bold',
                editable: true,
                borderColor: '#ff0000',
                cornerColor: '#ff0000',
                cornerSize: 15,
                transparentCorners: false,
                // Shadow for better readability
                shadow: new fabric.Shadow({
                    color: 'rgba(0,0,0,0.8)',
                    blur: 10,
                    offsetX: 2,
                    offsetY: 2
                })
            });

            // Adjust origin based on template assumption (center vs top-left)
            // Our backend config uses Top-Left X/Y usually, but aligns center text.
            // Fabric Textbox origin defaults to Top-Left.
            // If align is center, X should be the center point?
            // Let's stick to simple positioning first.

            fabricCanvas.add(textObj);
        });

        // Force render
        fabricCanvas.requestRenderAll();

    }, [fabricCanvas, config]);


    // Text Editing Controls (Toolbar)
    const updateActiveObject = (key, value) => {
        if (!activeObject) return;
        activeObject.set(key, value);
        fabricCanvas.requestRenderAll();
    };

    const handleSave = () => {
        setSaving(true);

        // Deselect everything to hide handles in output
        fabricCanvas.discardActiveObject();
        fabricCanvas.renderAll();

        const dataURL = fabricCanvas.toDataURL({
            format: 'png',
            quality: 0.9,
            multiplier: 1 // 1 = 1080x1350
        });

        // Convert DataURL to Blob
        fetch(dataURL)
            .then(res => res.blob())
            .then(blob => {
                const formData = new FormData();
                formData.append('image', blob, 'poster.png');

                return api.post(`cms/articles/${articleId}/save_poster/`, formData);
            })
            .then(res => {
                setSaving(false);
                if (onSaveSuccess) onSaveSuccess(res.data.url);
                if (onClose) onClose();
            })
            .catch(err => {
                console.error("Save failed", err);
                setSaving(false);
                alert("Failed to save poster");
            });
    };

    if (loading) {
        return (
            <div className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center text-white">
                <FaSpinner className="animate-spin text-4xl mb-4" />
                <p>Loading Poster Assets...</p>
            </div>
        );
    }

    return (
        <div className="fixed inset-0 bg-gray-900 z-50 flex overflow-hidden">
            {/* Sidebar Controls */}
            <div className="w-80 bg-gray-800 p-4 border-r border-gray-700 flex flex-col text-white overflow-y-auto">
                <div className="flex justify-between items-center mb-6">
                    <h2 className="text-xl font-bold">Poster Editor</h2>
                    <button onClick={onClose} className="text-gray-400 hover:text-white">
                        <FaTimes size={24} />
                    </button>
                </div>

                {/* Active Object Controls */}
                {activeObject && (activeObject.type === 'textbox' || activeObject.type === 'text') && (
                    <div className="mb-6 p-4 bg-gray-700 rounded-lg">
                        <h3 className="text-sm font-semibold mb-3 text-gray-300">Text Settings</h3>

                        <div className="space-y-3">
                            <div>
                                <label className="text-xs text-gray-400 block mb-1">Color</label>
                                <input
                                    type="color"
                                    className="w-full h-8 rounded cursor-pointer"
                                    value={activeObject.fill}
                                    onChange={(e) => updateActiveObject('fill', e.target.value)}
                                />
                            </div>

                            <div>
                                <label className="text-xs text-gray-400 block mb-1">Font Size</label>
                                <input
                                    type="range"
                                    min="20" max="200"
                                    value={activeObject.fontSize}
                                    onChange={(e) => updateActiveObject('fontSize', parseInt(e.target.value))}
                                    className="w-full"
                                />
                                <div className="text-right text-xs">{activeObject.fontSize}px</div>
                            </div>

                            <div>
                                <label className="text-xs text-gray-400 block mb-1">Text Align</label>
                                <div className="flex gap-2">
                                    {['left', 'center', 'right'].map(align => (
                                        <button
                                            key={align}
                                            onClick={() => updateActiveObject('textAlign', align)}
                                            className={`px-3 py-1 text-xs rounded border ${activeObject.textAlign === align ? 'bg-blue-600 border-blue-600' : 'border-gray-500 hover:bg-gray-600'}`}
                                        >
                                            {align.charAt(0).toUpperCase() + align.slice(1)}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                <div className="mt-auto">
                    <button
                        onClick={handleSave}
                        disabled={saving}
                        className="w-full py-4 bg-green-600 hover:bg-green-700 text-white font-bold rounded-lg flex items-center justify-center gap-2 transition-colors"
                    >
                        {saving ? <FaSpinner className="animate-spin" /> : <FaSave />}
                        Save & Publish
                    </button>
                </div>
            </div>

            {/* Canvas Area */}
            <div className="flex-1 bg-gray-900 flex items-center justify-center p-4 overflow-hidden relative">
                <div
                    className="shadow-2xl shadow-black relative"
                    style={{
                        transform: 'scale(0.5)', // Scale down to fit screen (1080px is tall)
                        transformOrigin: 'center center'
                    }}
                >
                    <canvas ref={canvasRef} />
                </div>

                {/* Zoom Hint */}
                <div className="absolute bottom-4 right-4 text-gray-500 text-sm pointer-events-none">
                    Canvas: 1080 x 1350 px (Scaled 50% for preview)
                </div>
            </div>
        </div>
    );
};

export default PosterEditor;
