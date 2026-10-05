import { GrahPage, grahMetadata } from "@/components/guides";

type Props = { params: Promise<{ graha: string }> };

export async function generateMetadata({ params }: Props) {
  return grahMetadata("hi", (await params).graha);
}

export default async function Page({ params }: Props) {
  return <GrahPage lang="hi" slug={(await params).graha} />;
}
