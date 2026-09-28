# TRISTAN OPERATING STATE

Generated: 2026-09-28 19:49:33

## HYPER

{
  "schema": "tristan.boost.state.r1",
  "node": "DESKTOP-2G1SSMT",
  "status": "ACTIVE",
  "ts": 1790639361.8355196,
  "expires_utc": "2026-09-29T09:04:02.4337846Z",
  "memory_load_pct": 55,
  "gpu": {
    "temp_c": 41,
    "util_pct": 0,
    "mem_used_mb": 0,
    "mem_total_mb": 8188
  },
  "events": [
    {
      "task": "git",
      "result": {
        "ok": true,
        "code": 0,
        "seconds": 70.02,
        "out": "{\n  \"node\": \"DESKTOP-2G1SSMT\",\n  \"private_auth\": \"PASS\",\n  \"summary\": {\n    \"CURRENT\": 44,\n    \"UPDATED\": 1\n  }\n}\n",
        "err": ""
      }
    }
  ],
  "last": {
    "git": 1790639361.8350017,
    "morph": 1790639276.7020876,
    "maintenance": 1790639258.5151405
  }
}

## GIT

{
  "schema": "tristan.git.autosync.receipt.r2",
  "ts": "2026-09-28T23:49:21Z",
  "node": "DESKTOP-2G1SSMT",
  "manifest_count": 45,
  "clone_budget_successes": 20,
  "private_auth": {
    "status": "PASS",
    "code": 0,
    "err": ""
  },
  "summary": {
    "CURRENT": 44,
    "UPDATED": 1
  },
  "repos": [
    {
      "name": "Tristan-Priv-",
      "full_name": "tardifmorencytristan-glitch/Tristan-Priv-",
      "path": "C:\\Users\\trist\\TristanRepos\\Tristan-Priv-",
      "ts": "2026-09-28T23:48:13Z",
      "branch": "main",
      "dirty": false,
      "head_before": "6dd6028e982fdbeb19446ceda30fb1f17641d1b9",
      "ahead": 0,
      "behind": 0,
      "action": "NO_ACTION",
      "status": "CURRENT",
      "head_after": "6dd6028e982fdbeb19446ceda30fb1f17641d1b9"
    },
    {
      "name": "Tristan-Tardif-Morency",
      "full_name": "tardifmorencytristan-glitch/Tristan-Tardif-Morency",
      "path": "C:\\Users\\trist\\TristanRepos\\Tristan-Tardif-Morency",
      "ts": "2026-09-28T23:48:15Z",
      "branch": "main",
      "dirty": false,
      "head_before": "2933a489385637cc2bd2046208f21a5280f2854b",
      "ahead": 0,
      "behind": 1,
      "action": "FF_ONLY",
      "status": "UPDATED",
      "pull_code": 0,
      "pull_err": "Updating files:  20% (1/5)\nUpdating files:  40% (2/5)\nUpdating files:  60% (3/5)\nUpdating files:  80% (4/5)\nUpdating files: 100% (5/5)\nUpdating files: 100% (5/5), done.\n",
      "head_after": "8ce7a58e042b5b7039e81755644b4d1fea4766e1"
    },
    {
      "name": "Tristan",
      "full_name": "tardifmorencytristan-glitch/Tristan",
      "path": "C:\\Users\\trist\\TristanRepos\\Tristan",
      "ts": "2026-09-28T23:48:21Z",
      "branch": "main",
      "dirty": false,
      "head_before": "7f78dbc88346dcab88e65e3aa4f289797ef22f97",
      "ahead": 0,
      "behind": 0,
      "action": "NO_ACTION",
      "status": "CURRENT",
      "head_after": "7f78dbc88346dcab88e65e3aa4f289797ef22f97"
    },
    {
      "name": "tristan-sovereign",
      "full_name": "tardifmorencytristan-glitch/tristan-sovereign",
      "path": "C:\\Users\\trist\\TristanRepos\\tristan-sovereign",
      "ts": "2026-09-28T23:48:22Z",
      "branch": "main",
      "dirty": false,
      "head_before": "f4d6374bef3869f8ce4aa84d43e65546af5250d6",
      "ahead": 0,
      "behind": 0,
      "action": "NO_ACTION",
      "status": "CURRENT",
      "head_after": "f4d6374bef3869f8ce4aa84d43e65546af5250d6"
    },
    {
      "name": "tristan-registry",
      "full_name": "tardifmorencytristan-glitch/tristan-registry",
      "path": "C:\\Users\\trist\\TristanRepos\\tristan-registry",
      "ts": "2026-09-28T23:48:24Z",
      "branch": "main",
      "dirty": false,
      "head_before": "b4b54f1bc7edf919dcc666c7ab5d6eef3ed3b951",
      "ahead": 0,
      "behind": 0,
      "action": "NO_ACTION",
      "status": "CURRENT",
      "head_after": "b4b54f1bc7edf919dcc666c7ab5d6eef3ed3b951"
    },
    {
      "name": "tristan-core",
      "full_name": "tardifmorencytristan-glitch/tristan-core",
      "path": "C:\\Users\\trist\\TristanRepos\\tristan-core",
      "ts": "2026-09-28T23:48:26Z",
      "branch": "main",
      "dirty": false,
      "head_before": "65d922239cff567ccfc2000deb9ab5a22deee6b8",
      "ahead": 0,
      "behind": 0,
      "action": "NO_ACTION",
      "status": "CURRENT",
      "head_after": "65d922239cff567ccfc2000deb9ab5a22deee6b8"
    },
    {
      "name": "tristan-hgfm",
      "full_name": "tardifmorencytristan-glitch/tristan-hgfm",
      "path": "C:\\Users\\trist\\TristanRepos\\tristan-hgfm",
      "ts": "2026-09-28T23:48:27Z",
      "branch": "main",
      "dirty": false,
      "head_before": "d11832d56b2dbcfc272afdfc63c24b78dc610e4b",
      "ahead": 0,
      "behind": 0,
      "action": "NO_ACTION",
      "status": "CURRENT",
      "head_after": "d11832d56b2dbcfc272afdfc63c24b78dc610e4b"
    },
    {
      "name": "tristan-cvcd",
      "full_name": "tardifmorencytristan-glitch/tristan-cvcd",
      "path": "C:\\Users\\trist\\TristanRepos\\tristan-cvcd",
      "ts": "2026-09-28T23:48:29Z",
      "branch": "main",
      "dirty": false,
      "head_before": "15b41da5c8a1c79f768fd0c1634ae082ca6651b7",
      "ahead": 0,
      "behind": 0,
      "action": "NO_ACTION",
      "status": "CURRENT",
      "head_after": "15b41da5c8a1c79f768fd0c1634ae082ca6651b7"
    },
    {
      "name": "tristan-ffwt",
      "full_name": "tardifmorencytristan-glitch/tristan-ffwt",
      "path": "C:\\Users\\trist\\TristanRepos\\tristan-ffwt",
      "ts": "2026-09-28T23:48:30Z",
      "branch": "main",
      "dirty": false,
      "head_before": "4032fedd782b7ed9dbd44a0777436c7e4af43b23",
      "ahead": 0,
      "behind": 0,
      "action": "NO_ACTION",
      "status": "CURRENT",
      "head_after": "4032fedd782b7ed9dbd44a0777436c7e4af43b23"
    },
    {
      "name": "tristan-t2",
      "full_name": "tardifmorencytristan-glitch/tristan-t2",
      "path": "C:\\Users\\trist\\TristanRepos\\tristan-t2",
      "ts": "2026-09-28T23:48:30Z",
      "branch": "main",
      "dirty": false,
      "head_before": "ca6995ffcd3b3bf331cc8709e1174d3181856b2c",
      "ahead": 0,
      "behind": 0,
      "action": "NO_ACTION",
      "status": "CURRENT",
      "head_after": "ca6995ffcd3b3bf331cc8709e1174d3181856b2c"
    },
    {
      "name": "tristan-oak",
      "full_name": "tardifmorencytristan-glitch/tristan-oak",
      "path": "C:\\Users\\trist\\TristanRepos\\tristan-oak",
      "ts": "2026-09-28T23:48:32Z",
      "branch": "main",
      "dirty": false,
      "head_before": "7a3c740d585538248ed4b0da0d33c39dfc0cd93b",
      "ahead": 0,
      "behind": 0,
      "action": "NO_ACTION",
      "status": "CURRENT",
      "head_after": "7a3c740d585538248ed4b0da0d33c39dfc0cd93b"
    },
    {
      "name": "tristan-anti-ego",
      "full_name": "tardifmorencytristan-glitch/tristan-anti-ego",
      "path": "C:\\Users\\trist\\TristanRepos\\tristan-anti-ego",
      "ts": "2026-09-28T23:48:33Z",
      "branch": "main",
      "dirty": false,
      "head_before": "a8d5ccfe8fe42afb809170b5a5c79c3b6f0e00ca",
      "ahead": 0,
      "behind": 0,
      "action": "NO_ACTION",
      "status": "CURRENT",
      "head_after": "a8d5ccfe8fe42afb809170b5a5c79c3b6f0e00ca"
    },
    {
      "name": "tristan-memory",
      "full_name": "tardifmorencytristan-glitch/tristan-memory",
      "path": "C:\\Users\\trist\\TristanRepos\\tristan-memory",
      "ts": "2026-09-28T23:48:34Z",
      "branch": "main",
      "dirty": false,
      "head_before": "bed6a04f63a1f10e2be82ccf8ab7acd72780ddf5",
      "ahead": 0,
      "behind": 0,
      "action": "NO_ACTION",
      "status": "CURRENT",
      "head_after": "bed6a04f63a1f10e2be82ccf8ab7acd72780ddf5"
    },
    {
      "name": "tristan-regeneration",
      "full_name": "tardifmorencytristan-glitch/tristan-regeneration",
      "path": "C:\\Users\\trist\\TristanRepos\\tristan-regeneration",
      "ts": "2026-09-28T23:48:36Z",
      "branch": "main",
      "dirty": false,
      "head_before": "71049f151c8af7fa72896096085f572266510410",
      "ahead": 0,
      "behind": 0,
      "action": "NO_ACTION",
      "status": "CURRENT",
      "head_after": "71049f151c8af7fa72896096085f572266510410"
    },
    {
      "name": "tristan-jarvis-core",
      "full_name": "tardifmorencytristan-glitch/tristan-jarvis-core",
      "path": "C:\\Users\\trist\\TristanRepos\\tristan-jarvis-core",
      "ts": "2026-09-28T23:48:38Z",
      "branch": "main",
      "dirty": false,
      "head_before": "7a99cf84db8cf81db0a0881c72d3482389445831",
      "ahead": 0,
      "behind": 0,
      "action": "NO_ACTION",
      "status": "CURRENT",
      "head_after": "7a99cf84db8cf81db0a0881c72d3482389445831"
    },
    {
      "name": "tristan-jarvis-windows",
      "full_name": "tardifmorencytristan-glitch/tristan-jarvis-windows",
      "path": "C:\\Users\\trist\\TristanRepos\\tristan-jarvis-windows",
      "ts": "2026-09-28T23:48:40Z",
      "branch": "main",
      "dirty": false,
      "head_before": "8522ca6a69705040445a17d980ba134a8988b456",
      "ahead": 0,
      "behind": 0,
      "action": "NO_ACTION",
      "status": "CURRENT",
      "head_after": "8522ca6a69705040445a17d980ba134a8988b456"
    },
    {
      "name": "tristan-jarvis-mobile",
      "full_name": "tardifmorencytristan-glitch/tristan-jarvis-mobile",
      "path": "C:\\Users\\trist\\TristanRepos\\tristan-jarvis-mobile",
      "ts": "2026-09-28T23:48:43Z",
      "branch": "main",
      "dirty": false,
      "head_before": "a15901d2783d13d7416227db32d532a1480feeb9",
      "ahead": 0,
      "behind": 0,
      "action": "NO_ACTION",
      "status": "CURRENT",
      "head_after": "a15901d2783d13d7416227db32d532a1480feeb9"
    },
    {
      "name": "tristan-jarvis-mesh",
      "full_name": "tardifmorencytristan-glitch/tristan-jarvis-mesh",
      "path": "C:\\Users\\trist\\TristanRepos\\tristan-jarvis-mesh",
      "ts": "2026-09-28T23:48:45Z",
      "branch": "main",
      "dirty": false,
      "head_before": "1a90b41fba7658e6ccd15f0d8456cbc65fa183de",
      "ahead": 0,
      "behind": 0,
      "action": "NO_ACTION",
      "status": "CURRENT",
      "head_after": "1a90b41fba7658e6ccd15f0d8456cbc65fa183de"
    },
    {
      "name": "tristan-virtual-compute",
      "full_name": "tardifmorencytristan-glitch/tristan-virtual-compute",
      "path": "C:\\Users\\trist\\TristanRepos\\tristan-virtual-compute",
      "ts": "2026-09-28T23:48:47Z",
      "branch": "main",
      "dirty": false,
      "head_before": "2d287c5c0b2803d61a7c9406c02be2991b1e5bbb",
      "ahead": 0,
      "behind": 0,
      "action": "NO_ACTION",
      "status": "CURRENT",
      "head_after": "2d287c5c0b2803d61a7c9406c02be2991b1e5bbb"
    },
    {
      "name": "tristan-resource-fabric",
      "full_name": "tardifmorencytristan-glitch/tristan-resource-fabric",
      "path": "C:\\Users\\trist\\TristanRepos\\tristan-resource-fabric",
      "ts": "2026-09-28T23:48:49Z",
      "branch": "main",
      "dirty": false,
      "head_before": "eb7a38cc9ecc29271d834608de7576b6bc34c164",
      "ahead": 0,
      "behind": 0,
      "action": "NO_ACTION",
      "status": "CURRENT",
      "head_after": "eb7a38cc9ecc29271d834608de7576b6bc34c164"
    },
    {
      "name": "tristan-reality",
      "full_name": "tardifmorencytristan-glitch/tristan-reality",
      "path": "C:\\Users\\trist\\TristanRepos\\tristan-reality",
      "ts": "2026-09-28T23:48:50Z",
      "branch": "main",
      "dirty": false,
      "head_before": "06740f061a6632895eb8c6bf2a9c12a56cd9705e",
      "ahead": 0,
      "behind": 0,
      "action": "NO_ACTION",
      "status": "CURRENT",
      "head_after": "06740f061a6632895eb8c6bf2a9c12a56cd9705e"
    },
    {
      "name": "tristan-git",
      "full_name": "tardifmorencytristan-glitch/tristan-git",
      "path": "C:\\Users\\trist\\TristanRepos\\tristan-git",
      "ts": "2026-09-28T23:48:52Z",
      "branch": "main",
      "dirty": false,
      "head_before": "646f3c0762a2b0c8daf0d1697dece6b721698704",
      "ahead": 0,
      "behind": 0,
      "action": "NO_ACTION",
      "status": "CURRENT",
      "head_after": "646f3c0762a2b0c8daf0d1697dece6b721698704"
    },
    {
      "name": "tristan-proof",
      "full_name": "tardifmorencytristan-glitch/tristan-proof",
      "path": "C:\\Users\\trist\\TristanRepos\\tristan-proof",
      "ts": "2026-09-28T23:48:53Z",
      "branch": "main",
      "dirty": false,
      "head_before": "4fda508097b2bd42f08d6fc71189392811d1b1bd",
      "ahead": 0,
      "behind": 0,
      "action": "NO_ACTION",
      "status": "CURRENT",
      "head_after": "4fda508097b2bd42f08d6fc71189392811d1b1bd"
    },
    {
      "name": "tristan-bench",
      "full_name": "tardifmorencytristan-glitch/tristan-bench",
      "path": "C:\\Users\\trist\\TristanRepos\\tristan-bench",
      "ts": "2026-09-28T23:48:54Z",
      "branch": "main",
      "dirty": false,
      "head_before": "e83af0b36423c3926f5960284da4e0a928300500",
      "ahead": 0,
      "behind": 0,
      "action": "NO_ACTION",
      "status": "CURRENT",
      "head_after": "e83af0b36423c3926f5960284da4e0a928300500"
    },
    {
      "name": "tristan-evidence",
      "full_name": "tardifmorencytristan-glitch/tristan-evidence",
      "path": "C:\\Users\\trist\\TristanRepos\\tristan-evidence",
      "ts": "2026-09-28T23:48:55Z",
      "branch": "main",
      "dirty": false,
      "head_before": "5b46dab3f9d4184d69db475817a762bee19cb4b1",
      "ahead": 0,
      "behind": 0,
      "action": "NO_ACTION",
      "status": "CURRENT",
      "head_after": "5b46dab3f9d4184d69db475817a762bee19cb4b1"
    },
    {
      "name": "tristan-physics",
      "full_name": "tardifmorencytristan-glitch/tristan-physics",
      "path": "C:\\Users\\trist\\TristanRepos\\tristan-physics",
      "ts": "2026-09-28T23:48:56Z",
      "branch": "main",
      "dirty": false,
      "head_before": "4dba1e0251119153b7d4f1f0a767fe9f42cf301f",
      "ahead": 0,
      "behind": 0,
      "action": "NO_ACTION",
      "status": "CURRENT",
      "head_after": "4dba1e0251119153b7d4f1f0a767fe9f42cf301f"
    },
    {
      "name": "tristan-materials",
      "full_name": "tardifmorencytristan-glitch/tristan-materials",
      "path": "C:\\Users\\trist\\TristanRepos\\tristan-materials",
      "ts": "2026-09-28T23:48:57Z",
      "branch": "main",
      "dirty": false,
      "head_before": "caafc84c3b652f6c0275b343994f8a7fbbb5ad4b",
      "ahead": 0,
      "behind": 0,
      "action": "NO_ACTION",
      "status": "CURRENT",
      "head_after": "caafc84c3b652f6c0275b343994f8a7fbbb5ad4b"
    },
    {
      "name": "tristan-chemistry",
      "full_name": "tardifmorencytristan-glitch/tristan-chemistry",
      "path": "C:\\Users\\trist\\TristanRepos\\tristan-chemistry",
      "ts": "2026-09-28T23:48:58Z",
      "branch": "main",
      "dirty": false,
      "head_before": "f7ad91646d05c8d4d4ffb7ffecc1d47c26405bfb",
      "ahead": 0,
      "behind": 0,
      "action": "NO_ACTION",
      "status": "CURRENT",
      "head_after": "f7ad91646d05c8d4d4ffb7ffecc1d47c26405bfb"
    },
    {
      "name": "tristan-biology",
      "full_name": "tardifmorencytristan-glitch/tristan-biology",
      "path": "C:\\Users\\trist\\TristanRepos\\tristan-biology",
      "ts": "2026-09-28T23:49:00Z",
      "branch": "main",
      "dirty": false,
      "head_before": "2c1bf3e5d8fdce5d43b51c22db9343045aeabf15",
      "ahead": 0,
      "behind": 0,
      "action": "NO_ACTION",
      "status": "CURRENT",
      "head_after": "2c1bf3e5d8fdce5d43b51c22db9343045aeabf15"
    },
    {
      "name": "tristan-health",
      "full_name": "tardifmorencytristan-glitch/tristan-health",
      "path": "C:\\Users\\trist\\TristanRepos\\tristan-health",
      "ts": "2026-09-28T23:49:01Z",
      "branch": "main",
      "dirty": false,
      "head_before": "89fed643f2bcda3febbc28d9b3cbecd00c558d45",
      "ahead": 0,
      "behind": 0,
      "action": "NO_ACTION",
      "status": "CURRENT",
      "head_after": "89fed643f2bcda3febbc28d9b3cbecd00c558d45"
    },
    {
      "name": "tristan-education",
      "full_name": "tardifmorencytristan-glitch/tristan-education",
      "path": "C:\\Users\\trist\\TristanRepos\\tristan-education",
      "ts": "2026-09-28T23:49:03Z",
      "branch": "main",
      "dirty": false,
      "head_before": "819cbe360e5f55c6f0e91f60bfc164c1e5b64975",
      "ahead": 0,
      "behind": 0,
      "action": "NO_ACTION",
      "status": "CURRENT",
      "head_after": "819cbe360e5f55c6f0e91f60bfc164c1e5b64975"
    },
    {
      "name": "tristan-economic",
      "full_name": "tardifmorencytristan-glitch/tristan-economic",
      "path": "C:\\Users\\trist\\TristanRepos\\tristan-economic",
      "ts": "2026-09-28T23:49:04Z",
      "branch": "main",
      "dirty": false,
      "head_before": "20aca9145b098101daec3c47fe4e43339806bf17",
      "ahead": 0,
      "behind": 0,
      "action": "NO_ACTION",
      "status": "CURRENT",
      "head_after": "20aca9145b098101daec3c47fe4e43339806bf17"
    },
    {
      "name": "tristan-research-factory",
      "full_name": "tardifmorencytristan-glitch/tristan-research-factory",
      "path": "C:\\Users\\trist\\TristanRepos\\tristan-research-factory",
      "ts": "2026-09-28T23:49:05Z",
      "branch": "main",
      "dirty": false,
      "head_before": "11c181c39cef65c957946846151b45ff74f00768",
      "ahead": 0,
      "behind": 0,
      "action": "NO_ACTION",
      "status": "CURRENT",
      "head_after": "11c181c39cef65c957946846151b45ff74f00768"
    },
    {
      "name": "tristan-patents-ip",
      "full_name": "tardifmorencytristan-glitch/tristan-patents-ip",
      "path": "C:\\Users\\trist\\TristanRepos\\tristan-patents-ip",
      "ts": "2026-09-28T23:49:07Z",
      "branch": "main",
      "dirty": false,
      "head_before": "3a2933e458672c6aa8ec81fd66a712678d857946",
      "ahead": 0,
      "behind": 0,
      "action": "NO_ACTION",
      "status": "CURRENT",
      "head_after": "3a2933e458672c6aa8ec81fd66a712678d857946"
    },
    {
      "name": "tristan-science",
      "full_name": "tardifmorencytristan-glitch/tristan-science",
      "path": "C:\\Users\\trist\\TristanRepos\\tristan-science",
      "ts": "2026-09-28T23:49:08Z",
      "branch": "main",
      "dirty": false,
      "head_before": "7fbf5020419da55bb16e8d4a62ade820d9bd2cf3",
      "ahead": 0,
      "behind": 0,
      "action": "NO_ACTION",
      "status": "CURRENT",
      "head_after": "7fbf5020419da55bb16e8d4a62ade820d9bd2cf3"
    },
    {
      "name": "tristan-revenue",
      "full_name": "tardifmorencytristan-glitch/tristan-revenue",
      "path": "C:\\Users\\trist\\TristanRepos\\tristan-revenue",
      "ts": "2026-09-28T23:49:10Z",
      "branch": "main",
      "dirty": false,
      "head_before": "5695ee97f1411d88a0bc2102b2f6f4f481486983",
      "ahead": 0,
      "behind": 0,
      "action": "NO_ACTION",
      "status": "CURRENT",
      "head_after": "5695ee97f1411d88a0bc2102b2f6f4f481486983"
    },
    {
      "name": "tristan-company",
      "full_name": "tardifmorencytristan-glitch/tristan-company",
      "path": "C:\\Users\\trist\\TristanRepos\\tristan-company",
      "ts": "2026-09-28T23:49:12Z",
      "branch": "main",
      "dirty": false,
      "head_before": "e4a8b50585496d155836e7ddd294df9c60161edf",
      "ahead": 0,
      "behind": 0,
      "action": "NO_ACTION",
      "status": "CURRENT",
      "head_after": "e4a8b50585496d155836e7ddd294df9c60161edf"
    },
    {
      "name": "tristan-polytechnique",
      "full_name": "tardifmorencytristan-glitch/tristan-polytechnique",
      "path": "C:\\Users\\trist\\TristanRepos\\tristan-polytechnique",
      "ts": "2026-09-28T23:49:13Z",
      "branch": "main",
      "dirty": false,
      "head_before": "592785fff24667ded6104825661a8349a44f40bf",
      "ahead": 0,
      "behind": 0,
      "action": "NO_ACTION",
      "status": "CURRENT",
      "head_after": "592785fff24667ded6104825661a8349a44f40bf"
    },
    {
      "name": "tristan-sdk-python",
      "full_name": "tardifmorencytristan-glitch/tristan-sdk-python",
      "path": "C:\\Users\\trist\\TristanRepos\\tristan-sdk-python",
      "ts": "2026-09-28T23:49:15Z",
      "branch": "main",
      "dirty": false,
      "head_before": "3c47065e88f6770d424e65dd6447f5323e83ac78",
      "ahead": 0,
      "behind": 0,
      "action": "NO_ACTION",
      "status": "CURRENT",
      "head_after": "3c47065e88f6770d424e65dd6447f5323e83ac78"
    },
    {
      "name": "tristan-sdk-js",
      "full_name": "tardifmorencytristan-glitch/tristan-sdk-js",
      "path": "C:\\Users\\trist\\TristanRepos\\tristan-sdk-js",
      "ts": "2026-09-28T23:49:16Z",
      "branch": "main",
      "dirty": false,
      "head_before": "9cadedb0df3b9ee803a148534c00633106650ef2",
      "ahead": 0,
      "behind": 0,
      "action": "NO_ACTION",
      "status": "CURRENT",
      "head_after": "9cadedb0df3b9ee803a148534c00633106650ef2"
    },
    {
      "name": "tristan-cli",
      "full_name": "tardifmorencytristan-glitch/tristan-cli",
      "path": "C:\\Users\\trist\\TristanRepos\\tristan-cli",
      "ts": "2026-09-28T23:49:16Z",
      "branch": "main",
      "dirty": false,
      "head_before": "045a2f54f83133b78bc2023472d47552462f7d10",
      "ahead": 0,
      "behind": 0,
      "action": "NO_ACTION",
      "status": "CURRENT",
      "head_after": "045a2f54f83133b78bc2023472d47552462f7d10"
    },
    {
      "name": "tristan-web",
      "full_name": "tardifmorencytristan-glitch/tristan-web",
      "path": "C:\\Users\\trist\\TristanRepos\\tristan-web",
      "ts": "2026-09-28T23:49:17Z",
      "branch": "main",
      "dirty": false,
      "head_before": "d0fbe0ab6a488f647e490b9d774299201844e949",
      "ahead": 0,
      "behind": 0,
      "action": "NO_ACTION",
      "status": "CURRENT",
      "head_after": "d0fbe0ab6a488f647e490b9d774299201844e949"
    },
    {
      "name": "tristan-public",
      "full_name": "tardifmorencytristan-glitch/tristan-public",
      "path": "C:\\Users\\trist\\TristanRepos\\tristan-public",
      "ts": "2026-09-28T23:49:18Z",
      "branch": "main",
      "dirty": false,
      "head_before": "c6ae172471dac76950613680b52d36ab32944fac",
      "ahead": 0,
      "behind": 0,
      "action": "NO_ACTION",
      "status": "CURRENT",
      "head_after": "c6ae172471dac76950613680b52d36ab32944fac"
    },
    {
      "name": "tristan-datasets",
      "full_name": "tardifmorencytristan-glitch/tristan-datasets",
      "path": "C:\\Users\\trist\\TristanRepos\\tristan-datasets",
      "ts": "2026-09-28T23:49:18Z",
      "branch": "main",
      "dirty": false,
      "head_before": "723b47d74e40d406f0b33622adfbe7e5970c4dbd",
      "ahead": 0,
      "behind": 0,
      "action": "NO_ACTION",
      "status": "CURRENT",
      "head_after": "723b47d74e40d406f0b33622adfbe7e5970c4dbd"
    },
    {
      "name": "tristan-oss-digest",
      "full_name": "tardifmorencytristan-glitch/tristan-oss-digest",
      "path": "C:\\Users\\trist\\TristanRepos\\tristan-oss-digest",
      "ts": "2026-09-28T23:49:20Z",
      "branch": "main",
      "dirty": false,
      "head_before": "c66588f4f295e1296ee9e595eedb5644db0ecd24",
      "ahead": 0,
      "behind": 0,
      "action": "NO_ACTION",
      "status": "CURRENT",
      "head_after": "c66588f4f295e1296ee9e595eedb5644db0ecd24"
    }
  ],
  "invariants": [
    "fetch-safe",
    "ff-only",
    "dirty=>HOLD",
    "ahead/diverged=>HOLD",
    "detached=>HOLD",
    "no-force-reset",
    "no-force-push",
    "no-credential-copy",
    "private-auth-failure=>skip-private"
  ]
}

## COCKPIT

{
  "schema": "tristan.autonomous.cockpit.supervisor.r1",
  "ts": "2026-09-28T22:07:00Z",
  "node": "DESKTOP-2G1SSMT",
  "tested": [
    {
      "release": 22,
      "path": "C:\\Users\\trist\\JarvisTristan\\gui\\jarvis_tristan_cockpit_r22.py",
      "ok": true,
      "code": 0
    }
  ],
  "previous_release": null,
  "authority": "local-user-scope",
  "status": "PASS",
  "selected_release": 22,
  "selected_path": "C:\\Users\\trist\\JarvisTristan\\gui\\jarvis_tristan_cockpit_r22.py",
  "selected_sha256": "2eccf14d66842b04fbd090c9598dd9c46c2b574729ed3a493491aa28b7855610",
  "self_test": {
    "ok": true,
    "code": 0,
    "output": "{\"status\": \"PASS\", \"schema\": \"jarvis-cockpit-r22-selftest\", \"node\": \"DESKTOP-2G1SSMT\", \"role\": \"OAK\", \"reality_source\": \"DIRECT_REALITY_R20\", \"reality_degraded\": false, \"truth_rows\": 3, \"contradictions\": 0, \"fleet_epoch\": {\"epoch_id\": \"c4867015315f98fb\", \"sample_count\": 3, \"spread_sec\": 4.799998760223389, \"coherent\": true}, \"state_capsule_inherited\": true, \"authority_granted\": false}\n"
  },
  "active_count": 1,
  "active": [
    {
      "ProcessId": 68672,
      "CommandLine": "C:\\Users\\trist\\AppData\\Local\\Programs\\Python\\Python313\\pythonw.exe C:\\Users\\trist\\JarvisTristan\\gui\\jarvis_tristan_cockpit_r22.py"
    }
  ],
  "promotion_rule": "highest-local-release-with-self-test-PASS"
}

## MORPH

{
  "schema": "tristan.residual.morphogenesis.derived.r1",
  "ts": 1790639362.0849366,
  "host": "DESKTOP-2G1SSMT",
  "source_receipt": "C:\\Users\\trist\\.tristan\\autonomous-maintenance\\receipts\\maintenance-20260928T234730Z.json",
  "capability_graph": {
    "node": "DESKTOP-2G1SSMT",
    "local_roots": [
      "C:\\Users\\trist\\JarvisTristan",
      "C:\\Users\\trist\\JARVIS_TRISTAN_LOCAL",
      "C:\\Users\\trist\\.tristan"
    ],
    "maintenance": "AVAILABLE",
    "cockpit": "VERIFIED",
    "repo_mode": "HOLD_DIRTY",
    "autonomy": "ACTIVE_OR_STARTED",
    "system_update_lane": "HOLD_ADMIN_CANARY_REQUIRED"
  },
  "weakness_atlas": [
    {
      "kind": "repo_dirty_hold",
      "severity": 0.7,
      "centrality": 0.7,
      "uncertainty": 0.2,
      "repairability": 0.8,
      "priority": 0.49,
      "evidence": {
        "path": "C:\\Users\\trist\\TristanCanonical",
        "action": "HOLD_DIRTY",
        "ok": false
      },
      "route": "REVIEW_LOCAL_CHANGES"
    },
    {
      "kind": "admin_update_lane_missing",
      "severity": 0.5,
      "centrality": 0.65,
      "uncertainty": 0.25,
      "repairability": 0.5,
      "priority": 0.2708,
      "evidence": "HOLD_ADMIN_CANARY_REQUIRED",
      "route": "CANARY_ADMIN_LANE"
    }
  ],
  "operator_routes": [
    {
      "residual": "repo_dirty_hold",
      "candidate_operators": [
        "GitTristan",
        "KEEP_SEPARATE",
        "NO_ACTION"
      ],
      "selection_rule": "maximize verified closure / (cost+risk+complexity+proof_debt)"
    },
    {
      "residual": "admin_update_lane_missing",
      "candidate_operators": [
        "canary",
        "snapshot",
        "rollback",
        "HOLD"
      ],
      "selection_rule": "maximize verified closure / (cost+risk+complexity+proof_debt)"
    }
  ],
  "capability_crystals": [
    {
      "capability_id": "verified-local-cockpit",
      "status": "MERGEABLE_DERIVED_CAPABILITY",
      "source": "C:\\Users\\trist\\.tristan\\autonomous-maintenance\\receipts\\maintenance-20260928T234730Z.json",
      "mechanism": "highest local cockpit release passing self-test",
      "integration": "retain current verified cockpit",
      "rollback": "previous verified cockpit release",
      "authority": "local user scope only"
    }
  ],
  "decision_policy": {
    "order": [
      "REUSE",
      "COMPOSE",
      "PATCH_EXISTING",
      "CREATE",
      "NO_ACTION"
    ],
    "terminal_states": [
      "MERGED",
      "PATCH_EXISTING",
      "COMPOSE",
      "KEEP_SEPARATE",
      "HOLD",
      "REJECT",
      "SUPERSEDED",
      "RESIDUAL",
      "UNAVAILABLE",
      "NO_ACTION"
    ],
    "merge_requires": [
      "evidence",
      "tests",
      "compatibility",
      "authority",
      "rollback",
      "provenance"
    ],
    "anti_ego": [
      "OriginBonus=0",
      "Capability!=Authority",
      "Generated!=Verified",
      "NO_ACTION admissible"
    ]
  }
}

## WORKER

{
  "schema": "tristan.workertruth.r1",
  "nodeID": "DESKTOP-2G1SSMT",
  "inputHash": "f61394ff3acae4c57a08ea149e495eca9d137ceafaa35e1aa336c0e83d65d078",
  "planHash": "3b199fcda50f0583d4d8906c4d81e7a6f189913bfc46785f5f52a01bc7a9556c",
  "resultHash": "5568d39feec548f0180d265d10f8f29f65d775050b3c03ae7d575e2b4c18cf01",
  "genomeHash": "4685ac4060daf74e80b6bc85a66a28b6c1b35a5174258ddb9db04f237c6c2c45",
  "timestamps": {
    "verified_at_unix": 1790639364.658882
  },
  "verifierResult": "PASS",
  "authorityGranted": false,
  "courtDecision": {
    "event_envelope": "COMPOSE_CLOUDEVENTS_FIELDS",
    "telemetry": "KEEP_SEPARATE_CHALLENGER_OTEL",
    "inventory": "KEEP_SEPARATE_CHALLENGER_OSQUERY",
    "capability_protocol": "COMPOSE_MCP_CONCEPTS_NOT_FULL_RUNTIME",
    "runtime_install": "NO_ACTION_UNTIL_REAL_WORKLOAD_WIN"
  },
  "cockpitStatus": "VERIFIED"
}

## FLEET

{
  "schema": "tristan.fleet.workertruth.r1",
  "planHash": "3b199fcda50f0583d4d8906c4d81e7a6f189913bfc46785f5f52a01bc7a9556c",
  "genomeHash": "4685ac4060daf74e80b6bc85a66a28b6c1b35a5174258ddb9db04f237c6c2c45",
  "verifierResult": "PASS_3_OF_3",
  "nodes": [
    {
      "nodeID": "DESKTOP-SHA9IHL",
      "inputHash": "cfb4e1ca97c5316448906e1408c1d363029c8d57b32df72b612f62f802344b73",
      "resultHash": "fb58f6c0e32aef4a2fc25ee3156e9c8c8f9f9cfa1b2a6aea1bfd2c4309449cdc"
    },
    {
      "nodeID": "DESKTOP-2G1SSMT",
      "inputHash": "b5469dc8f2afdf822017a66a46c7d04b4e5421200564fe90db49c00ca47c4729",
      "resultHash": "273a5f06f278ce54dffeb16d5bff23d10e90111cbe1b6e16f6adfe8999955d37"
    },
    {
      "nodeID": "LAPTOP-AIU36QN6",
      "inputHash": "f0174d81e914db9bf0d5a5110e65a0fc149f88521d15e5f2d939f85a60284f5e",
      "resultHash": "76f0fa4a7bbb26920f5f7efa5486e2c3a64ff7355f77e4a3519e225a838c8b44"
    }
  ],
  "decision": {
    "event_envelope": "COMPOSE_CLOUDEVENTS_FIELDS",
    "capability_protocol": "COMPOSE_MCP_CONCEPTS_NOT_FULL_RUNTIME",
    "telemetry": "KEEP_SEPARATE_CHALLENGER_OTEL",
    "inventory": "KEEP_SEPARATE_CHALLENGER_OSQUERY",
    "runtime_install": "NO_ACTION_UNTIL_REAL_WORKLOAD_WIN"
  },
  "authorityGranted": false,
  "limits": [
    "same-user 3-node local court",
    "schema-level mechanism benchmark",
    "not full external runtime benchmark"
  ]
}

