<template>
	<keep-alive include="RecorderDetail">
		<router-view/>
	</keep-alive>
</template>

<script>
export default {
	name: "RecorderRoot",
	watch: {
		$route() {
			vmraid.router.current_route = vmraid.router.parse();
			vmraid.breadcrumbs.update();
		}
	}
};
</script>
