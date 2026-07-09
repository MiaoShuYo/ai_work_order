<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useDocumentsStore } from '../../stores/documents'

const store = useDocumentsStore()
const fileInput = ref<HTMLInputElement>()
const isDragOver = ref(false)
// 用文件名做 key 记录每个文件各自的上传进度，支持同时拖拽多个文件上传。
const uploadProgress = reactive<Record<string, number>>({})

async function uploadFiles(files: FileList | File[]) {
    for (const file of Array.from(files)) {
        uploadProgress[file.name] = 0
        try {
            await store.uploadDocument(file, (percent) => {
                uploadProgress[file.name] = percent
            })
        } finally {
            delete uploadProgress[file.name]
        }
    }
}

function onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement
    if (input.files?.length) {
        uploadFiles(input.files)
        input.value = ''
    }
}

function onDrop(event: DragEvent) {
    event.preventDefault()
    isDragOver.value = false
    if (event.dataTransfer?.files.length) {
        uploadFiles(event.dataTransfer.files)
    }
}

function onDragOver(event: DragEvent) {
    // 浏览器默认行为是直接打开被拖拽的文件，不调用 preventDefault 拖拽上传不会触发 drop 事件。
    event.preventDefault()
    isDragOver.value = true
}
</script>

<template>
    <div class="upload-zone" :class="{ 'upload-zone-active': isDragOver }" @dragover="onDragOver"
        @dragleave="isDragOver = false" @drop="onDrop">
        <p>将文件拖拽到此处，或者</p>
        <button type="button" @click="fileInput?.click()">点击选择文件</button>
        <input ref="fileInput" type="file" multiple hidden @change="onFileSelected" />
        <div v-for="(percent, name) in uploadProgress" :key="name" class="progress-row">
            <span class="progress-name">{{ name }}</span>
            <div class="progress-bar">
                <div class="progress-bar-inner" :style="{ width: percent + '%' }"></div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.upload-zone {
    border: 2px dashed #d1d5db;
    border-radius: 8px;
    padding: 24px;
    text-align: center;
    transition: border-color 0.2s;
}

.upload-zone-active {
    border-color: #2563eb;
    background-color: #eff6ff;
}

.progress-row {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 8px;
    font-size: 13px;
}

.progress-name {
    flex-shrink: 0;
    width: 120px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.progress-bar {
    flex: 1;
    height: 6px;
    background-color: #e5e7eb;
    border-radius: 3px;
    overflow: hidden;
}

.progress-bar-inner {
    height: 100%;
    background-color: #2563eb;
    transition: width 0.2s;
}
</style>