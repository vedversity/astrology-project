import { GrahPage, grahMetadata } from "@/components/guides";

type Props = { params: Promise<{ graha: string }> };

export async function generateMetadata({ params }: Props) {
  return grahMetadata("en", (await params).graha);
}

export default async function Page({ params }: Props) {
  return <GrahPage lang="en" slug={(await params).graha} />;
}
