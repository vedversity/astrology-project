import { DoshPage, doshMetadata } from "@/components/guides";

type Props = { params: Promise<{ dosha: string }> };

export async function generateMetadata({ params }: Props) {
  return doshMetadata("hi", (await params).dosha);
}

export default async function Page({ params }: Props) {
  return <DoshPage lang="hi" slug={(await params).dosha} />;
}
