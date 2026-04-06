interface ItemImageUploadProps {
  isPending: boolean
  hasImage: boolean
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void
}

export function ItemImageUpload({ isPending, hasImage, onChange }: ItemImageUploadProps) {
  return (
    <label
      className={`flex flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed px-4 py-6 text-sm transition-colors cursor-pointer
      ${isPending ? 'opacity-50 pointer-events-none' : 'hover:border-primary hover:bg-muted/50'}`}
    >
      {isPending ? (
        <>
          <div className="h-5 w-5 animate-spin rounded-full border-2 border-primary border-t-transparent" />
          <span className="text-muted-foreground">Uploading…</span>
        </>
      ) : (
        <>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-8 w-8 text-muted-foreground"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={1.5}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5"
            />
          </svg>
          <span className="font-medium">{hasImage ? 'Replace image' : 'Upload image'}</span>
          <span className="text-muted-foreground text-xs">PNG, JPG, WEBP up to any size</span>
        </>
      )}
      <input type="file" accept="image/*" onChange={onChange} className="hidden" />
    </label>
  )
}
