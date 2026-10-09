import Image from "next/image";

export default function UnsplashBackground({ imageId, opacity = "bg-slate-950/80" }) {
  return (
    <div className="absolute inset-0 z-0 pointer-events-none">
      <Image
        src={`https://images.unsplash.com/photo-${imageId}?auto=format&fit=crop&w=2000&q=80`}
        alt="Background"
        fill
        className="object-cover"
        priority
      />
      <div className={`absolute inset-0 ${opacity} backdrop-blur-[2px] transition-all`} />
    </div>
  );
}