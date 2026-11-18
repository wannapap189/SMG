import fs from 'node:fs/promises';
import path from 'node:path';
import {mergeDuplicateProducts} from './catalog-duplicates.mjs';

// Match explicit product status, never infer availability from listing age.
const unavailable = /sold\s*out|out[\s-]*of[\s-]*stock|discontinued|สินค้าหมด|หมดแล้ว|หมดสต[็๊]อก|ยกเลิกการผลิต|เลิกผลิต|ยุติการผลิต|停[产產]|售罄|售完|缺[货貨]/i;
export async function prepareCatalog(root) {
  const dataPath=path.join(root,'data/catalog.json');
  const data=JSON.parse(await fs.readFile(dataPath,'utf8'));
  const archivePath=path.resolve('../catalog-import/unavailable-products.json');
  let archive=[];
  try{archive=JSON.parse(await fs.readFile(archivePath,'utf8'));}catch(e){if(e.code!=='ENOENT')throw e;}
  mergeDuplicateProducts(data,archive);
  const blocked=new Set(archive.map(p=>p.id));
  for(const p of data.items){
    const evidence=[p.name,p.titleTh,p.catalogStatusTh,p.availability,p.stockStatus].filter(Boolean).join('\n');
    if(unavailable.test(evidence)&&!blocked.has(p.id)){
      archive.push({...p,removedAt:'2026-11-18',removalReason:'ต้นทางระบุหมดสินค้าหรือยุติการผลิต',availabilityEvidence:evidence});
      blocked.add(p.id);
    }
  }
  data.items=data.items.filter(p=>!blocked.has(p.id));
  await fs.writeFile(archivePath,JSON.stringify(archive,null,2));
  await fs.writeFile(dataPath,JSON.stringify(data));
  const featuredPath=path.join(root,'data/featured.json');
  const featured=JSON.parse(await fs.readFile(featuredPath,'utf8')).filter(p=>!blocked.has(p.id));
  await fs.writeFile(featuredPath,JSON.stringify(featured));
  const categoryPath=path.join(root,'data/categories.json');
  const categories=JSON.parse(await fs.readFile(categoryPath,'utf8'));
  for(const c of categories)c.count=data.items.filter(p=>p.categories.includes(c.slug)).length;
  await fs.writeFile(categoryPath,JSON.stringify(categories));
  return archive;
}
